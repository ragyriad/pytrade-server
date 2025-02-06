import yaml
from pathlib import Path
import calendar
from datetime import timezone, datetime
import re
import traceback
import uuid

from questrade_api import Questrade
from database.models import Account, Activity, Security
from helpers.helpers import safeBulkCreate, openFile, writeFile, formatFileName
from data.constants import (
    SECURITY_UPDATE_FIELDS,
    SECURITY_UNIQUE_FIELD,
    ACCOUNTPOSITION_UNIQUE_FIELD,
    ACCOUNTPOSITION_UPDATE_FIELDS,
    ACTIVITY_UNIQUE_FIELD,
    ACTIVITY_UPDATE_FIELDS,
)
from ..data.constants import QUESTRADE_ACTIVITY_TYPE_DICT

from django.http import JsonResponse

base_path = Path(__file__).parent
file_path = (base_path / "info/questrade.yaml").resolve()


def getActivityAction(activity):
    if activity["type"] == "Trades":
        value = float(activity["netAmount"])
        if value > 0:
            return "Sell"
        elif value < 0:
            return "Buy"
        else:
            return None


def authentication():
    print("Authenticating Questrade")
    fileContent = openFile(file_path)
    questObject = Questrade()

    try:
        questObject = Questrade(refresh_token=fileContent["refresh_token"])
    except Exception as e:
        print("Response")
        print(e)
        print("Most likely you will need a new refresh token")

    modifiedQuestradeInfo = fileContent
    modifiedQuestradeInfo["refresh_token"] = questObject.auth.token["refresh_token"]
    modifiedQuestradeInfo["access_token"] = questObject.auth.token["access_token"]
    modifiedQuestradeInfo["api_server"] = questObject.auth.token["api_server"]
    writeFile(file_path, modifiedQuestradeInfo)
    return questObject


def syncQestradeAccounts(request):
    questradeObject = authentication()
    try:
        accounts = questradeObject.accounts["accounts"]
        accountObjToSave = [
            Account(
                type=account["type"],
                account_number=account["number"],
                status=account["status"],
                is_primary=account["isPrimary"],
                last_synced=datetime.now(),
                currency="CAD",
                account_broker_id="Questrade",
            )
            for account in accounts
        ]
        Account.objects.bulk_create(accountObjToSave)
        return JsonResponse(
            {"count": len(accounts), "Saved Accounts": accounts},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print(e.args)
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def syncQuestradeActivities(request):
    try:
        questradeObject = authentication()
        fetchedAccounts = AccountSerializer(
            Account.objects.filter(account_number__in=["51978003", "51983522"]),
            many=True,
        ).data
        activitiesToSave = []
        securitiesToSave = []
        security_list = []
        for account in fetchedAccounts:

            account_number = account["account_number"]
            print(
                "\n Updating "
                + account["type"]
                + " Account# "
                + account["account_number"]
                + "\n"
            )
            startingYear = 2019
            for year in range(startingYear, 2024):
                for month in range(1, 13):
                    lastDayOfMonth = calendar.monthrange(year, month)[1]
                    queryStartTime = datetime(year, month, 1, tzinfo=timezone.utc)
                    queryEndTime = datetime(
                        year, month, lastDayOfMonth, tzinfo=timezone.utc
                    )
                    print(
                        account["type"]
                        + " Account# "
                        + account["account_number"]
                        + " Request Period "
                        + str(queryStartTime).split(" ")[0]
                        + "-"
                        + str(queryEndTime).split(" ")[0]
                    )
                    response = questradeObject.account_activities(
                        account_number, startTime=queryStartTime, endTime=queryEndTime
                    )
                    activities = response["activities"]

                    print("Found " + str(len(activities)) + " activities")
                    optionsPattern = "^.*\d{1,2}[A-Za-z]{3}\d{2}P\d{1,}\.\d{2}$"
                    for activity in activities:

                        match = re.match(optionsPattern, activity["symbol"])

                        activityType = ""
                        if match:
                            activityType = "Option"
                        elif activity["type"] == "Trades":
                            activityType = "Order"
                        else:
                            activityType = activity["type"]

                        security_list = [
                            getattr(security, "id") for security in securitiesToSave
                        ]

                        if (
                            activity["type"] == "Trades"
                            and "symbolId" in activity
                            and activity["symbolId"] not in security_list
                        ):
                            securitiesToSave.append(
                                Security(
                                    id=activity["symbolId"],
                                    currency=activity["currency"],
                                    symbol=activity["symbol"],
                                    type=(
                                        activityType
                                        if activityType == "Option"
                                        else "Equity"
                                    ),
                                )
                            )

                        activitiesToSave.append(
                            Activity(
                                id=(
                                    activity["id"]
                                    if "id" in activity
                                    else uuid.uuid4().hex
                                ),
                                currency=activity["currency"],
                                type=QUESTRADE_ACTIVITY_TYPE_DICT[activityType],
                                action=getActivityAction(activity),
                                price=activity["price"],
                                quantity=activity["quantity"],
                                amount=activity["netAmount"],
                                commission=activity["commission"],
                                symbol=activity["symbol"],
                                submitted_at=activity["settlementDate"],
                                filled_at=activity["tradeDate"],
                                security_id=(
                                    activity["symbolId"]
                                    if (
                                        activity["type"] == "Trades"
                                        and "symbolId" in activity
                                    )
                                    else None
                                ),
                                account_id=account_number,
                            )
                        )

        securityRecords = safeBulkCreate(
            Security,
            securitiesToSave,
            uniqueField=SECURITY_UNIQUE_FIELD,
            updateFields=SECURITY_UPDATE_FIELDS,
        )
        securityRecords = SecuritySerializer(securityRecords, many=True).data
        activityRecords = safeBulkCreate(
            Activity,
            activitiesToSave,
            uniqueField=ACTIVITY_UNIQUE_FIELD,
            updateFields=ACTIVITY_UPDATE_FIELDS,
        )
        activityRecords = ActivitySerializer(activityRecords, many=True).data
        return JsonResponse(
            {
                "security_count": len(securityRecords),
                "security": securityRecords,
                "activity_count": len(activityRecords),
                "activity": activityRecords,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print(e.args)
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
