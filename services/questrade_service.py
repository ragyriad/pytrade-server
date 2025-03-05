import calendar
import re
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.models import Account, Activity, Security
from repositories.base_repository import BaseRepository
from database.session import get_db

from data.constants import (
    SECURITY_UPDATE_FIELDS,
    SECURITY_UNIQUE_FIELD,
    ACTIVITY_UNIQUE_FIELD,
    ACTIVITY_UPDATE_FIELDS,
    QUESTRADE_ACTIVITY_TYPE_DICT,
)
from database.schemas import AccountResponse, ActivityResponse

router = APIRouter()
base_path = Path(__file__).parent
file_path = (base_path / "brokers/questrade.yaml").resolve()

from utils.utils import open_file, write_file
from questrade_api import Questrade


def auth():
    print("Authenticating Questrade")
    file_content = open_file(file_path)

    try:
        quest_object = Questrade(refresh_token=file_content["refresh_token"])
    except Exception as e:
        print("Authentication failed:", e)
        raise HTTPException(
            status_code=401, detail="Invalid refresh token. Generate a new one."
        )

    # Update stored tokens
    file_content.update(
        {
            "refresh_token": quest_object.auth.token["refresh_token"],
            "access_token": quest_object.auth.token["access_token"],
            "api_server": quest_object.auth.token["api_server"],
        }
    )
    write_file(file_path, file_content)

    return quest_object


def get_activity_action(activity):
    if activity["type"] == "Trades":
        value = float(activity["netAmount"])
        return "Sell" if value > 0 else "Buy" if value < 0 else None


def sync_accounts(db: Session = Depends(get_db)):
    questrade = auth()

    try:
        accounts = questrade.accounts["accounts"]
        account_objs = [
            Account(
                type=acc["type"],
                account_number=acc["number"],
                status=acc["status"],
                is_primary=acc["isPrimary"],
                last_synced=datetime.now(),
                currency="CAD",
                account_broker_id="Questrade",
            )
            for acc in accounts
        ]
        db.bulk_save_objects(account_objs)
        db.commit()

        return {"count": len(accounts), "saved_accounts": accounts}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


def sync_activities(db: Session = Depends(get_db)):
    """Fetch and sync Questrade activities."""
    try:
        questrade = auth()
        fetched_accounts = (
            db.query(Account)
            .filter(Account.account_number.in_(["51978003", "51983522"]))
            .all()
        )

        activities_to_save = []
        securities_to_save = []
        security_ids = set()

        for account in fetched_accounts:
            account_number = account.account_number
            print(f"\nUpdating {account.type} Account# {account_number}\n")

            for year in range(2019, 2024):
                for month in range(1, 13):
                    last_day = calendar.monthrange(year, month)[1]
                    start_time = datetime(year, month, 1, tzinfo=timezone.utc)
                    end_time = datetime(year, month, last_day, tzinfo=timezone.utc)

                    print(
                        f"{account.type} Account# {account_number} Request Period {start_time.date()} - {end_time.date()}"
                    )

                    response = questrade.account_activities(
                        account_number, startTime=start_time, endTime=end_time
                    )
                    activities = response["activities"]

                    print(f"Found {len(activities)} activities")
                    options_pattern = r"^.*\d{1,2}[A-Za-z]{3}\d{2}P\d{1,}\.\d{2}$"

                    for activity in activities:
                        is_option = bool(re.match(options_pattern, activity["symbol"]))
                        activity_type = (
                            "Option"
                            if is_option
                            else (
                                "Order"
                                if activity["type"] == "Trades"
                                else activity["type"]
                            )
                        )

                        if (
                            activity["type"] == "Trades"
                            and "symbolId" in activity
                            and activity["symbolId"] not in security_ids
                        ):
                            securities_to_save.append(
                                Security(
                                    id=activity["symbolId"],
                                    currency=activity["currency"],
                                    symbol=activity["symbol"],
                                    type="Option" if is_option else "Equity",
                                )
                            )
                            security_ids.add(activity["symbolId"])

                        activities_to_save.append(
                            Activity(
                                id=activity.get("id", uuid.uuid4().hex),
                                currency=activity["currency"],
                                type=QUESTRADE_ACTIVITY_TYPE_DICT.get(
                                    activity_type, "Unknown"
                                ),
                                action=get_activity_action(activity),
                                price=activity.get("price"),
                                quantity=activity.get("quantity"),
                                amount=activity.get("netAmount"),
                                commission=activity.get("commission"),
                                symbol=activity.get("symbol"),
                                submitted_at=activity.get("settlementDate"),
                                filled_at=activity.get("tradeDate"),
                                security_id=(
                                    activity.get("symbolId")
                                    if activity["type"] == "Trades"
                                    else None
                                ),
                                account_id=account_number,
                            )
                        )
        security_repo = BaseRepository(db, Security)
        activity_repo = BaseRepository(db, Activity)
        # Bulk insert securities and activities
        security_repo.safe_bulk_create(
            db,
            Security,
            securities_to_save,
            SECURITY_UNIQUE_FIELD,
            SECURITY_UPDATE_FIELDS,
        )
        activity_repo.safe_bulk_create(
            db,
            Activity,
            activities_to_save,
            ACTIVITY_UNIQUE_FIELD,
            ACTIVITY_UPDATE_FIELDS,
        )

        return {
            "security_count": len(securities_to_save),
            "activity_count": len(activities_to_save),
        }

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))


def sync_with_questrade(db: Session = Depends(get_db)):
    try:
        account_sync_result = sync_accounts(db)
        activity_sync_result = sync_activities(db)

        return {
            "accounts_synced": account_sync_result["count"],
            "activities_synced": activity_sync_result["activity_count"],
        }

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))
