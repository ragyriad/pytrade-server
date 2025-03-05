import asyncio
from data.constants import WSIMPLE_ACTIVITY_TYPE_DICT
from database.schemas import ActivityCreate, SecurityCreate
from database.models import Account, Activity, Security
from repositories.base_repository import BaseRepository
from brokers.wealthsimple.wealthSimple import wealthSimple

from data.constants import (
    SECURITY_UNIQUE_FIELD,
    SECURITY_UPDATE_FIELDS,
    ACTIVITY_UNIQUE_FIELD,
    ACTIVITY_UPDATE_FIELDS,
    WEALTHSIMPLE_ACTIVITIES_TYPES,
    WSIMPLE_ACTIVITY_TYPE_DICT,
)


def clean_fetch_activities_data(activities):
    activitiesObjList = []
    securitiesObjList = []

    for activity in activities:
        print(activity)
        actionFnData = {
            "object": activity["object"],
            "orderType": activity["order_type"] if "order_type" in activity else None,
            "autoOrderType": (
                activity["auto_order_type"] if "auto_order_type" in activity else None
            ),
        }
        amountValue = setActivityAmountValue(activity)
        symbolVal = activity["symbol"] if "symbol" in activity else None

        accountIdVal = ""
        if "internal_transfer" in activity:
            accountIdVal = activity["destination_account_id"]
        if "account_id" in activity:
            accountIdVal = activity["account_id"]
        marketCurrency = ""
        if "market_currency" in activity:
            marketCurrency = activity["market_currency"]
        elif "net_cash" in activity:
            marketCurrency = activity["net_cash"]["currency"]
        else:
            marketCurrency = None
        activityObj = Activity(
            id=activity["id"],
            currency=setActivityCurrency(activity),
            type=WSIMPLE_ACTIVITY_TYPE_DICT[activity["object"]],
            sub_type=(
                activity["order_sub_type"] if "order_sub_type" in activity else None
            ),
            action=getActivityAction(actionFnData),
            stop_price=activity["stop_price"] if "stop_price" in activity else 0,
            price=setActivityPrice(activity),
            quantity=activity["quantity"] if "quantity" in activity else 0,
            symbol=symbolVal,
            amount=amountValue,
            commission=(
                activity["filledTotalTransactionFee"]["amount"]
                if "filledTotalTransactionFee" in activity
                else 0
            ),
            option_multiplier=(
                activity["option_multiplier"]
                if "option_multiplier" in activity
                else None
            ),
            market_currency=marketCurrency,
            status=activity["status"] if "status" in activity else None,
            cancelled_at=(
                activity["cancelled_at"] if "cancelled_at" in activity else None
            ),
            rejected_at=activity["rejected_at"] if "rejected_at" in activity else None,
            submitted_at=(
                activity["submitted_at"] if "submitted_at" in activity else None
            ),
            filled_at=activity["filled_at"] if "filled_at" in activity else None,
            account_id=accountIdVal,
            security_id=activity["security_id"] if "security_id" in activity else None,
        )
        activitiesObjList.append(activityObj)
        if "security_id" in activity and activity["security_id"] not in (
            getattr(security, "id") for security in securitiesObjList
        ):
            securityObj = Security(
                id=activity["security_id"],
                symbol=symbolVal,
                name=activity["security_name"],
                currency=setActivityCurrency(activity),
            )
            securitiesObjList.append(securityObj)
    return activitiesObjList, securitiesObjList


async def sync_wealthsimple_data(db):
    """
    Sync all data from Wealthsimple (securities, activities, etc.)
    """
    ws_instance = await get_ws_connection()

    securities_data = ws_instance.get_securities()
    securities = [SecurityCreate(**s) for s in securities_data]
    security_repo = BaseRepository(db, Security)
    activity_repo = BaseRepository(db, Activity)
    security_repo.safe_bulk_create(
        securities, SECURITY_UNIQUE_FIELD, SECURITY_UPDATE_FIELDS
    )

    activities_data = await fetch_activities_async(ws_instance)
    activities, securities = clean_fetch_activities_data(activities_data)

    security_repo.safe_bulk_create(
        securities, SECURITY_UNIQUE_FIELD, SECURITY_UPDATE_FIELDS
    )
    count = activity_repo.safe_bulk_create(
        activities, ACTIVITY_UNIQUE_FIELD, ACTIVITY_UPDATE_FIELDS
    )

    return count, "Wealthsimple data synchronized successfully"


async def fetch_activities_async(ws_instance):
    """
    Fetches all Wealthsimple activities asynchronously
    """
    tasks = []
    for activity_type in WEALTHSIMPLE_ACTIVITIES_TYPES:
        if activity_type != "all":
            tasks.append(
                ws_instance.get_activities({"limit": 99, "type": activity_type})
            )
    return await asyncio.gather(*tasks)


async def get_ws_connection(session_id=None, mfa_code=None):
    """
    Retrieves or initializes a Wealthsimple connection.
    """
    instance = get_instance_cache(session_id)
    if not instance:
        ws_config = load_wsimple_config()
        new_instance = wealthSimple(
            email=ws_config["email"], password=ws_config["password"], mfa_code=mfa_code
        )
        set_instance_cache(
            new_instance.box.access_token, new_instance, new_instance.box.access_expires
        )
        return new_instance
    return instance


def get_activity_action(action_dict: dict) -> str:
    """Determines the activity action based on order type and object type."""
    object_type, order_type, auto_order_type = (
        action_dict.get("object"),
        action_dict.get("orderType"),
        action_dict.get("autoOrderType"),
    )

    if object_type == "dividend":
        return "DRIP" if auto_order_type == "dividend_reinvestment" else "Cash Dividend"

    return order_type.split("_")[0].capitalize() if order_type else None


def get_activity_amount_value(data: dict) -> float:
    """Extracts the correct amount value based on the activity type."""
    if "filled_net_value" in data:
        return data["filled_net_value"]
    if data.get("object") == "dividend":
        return data["net_cash"]["amount"]
    return None


def get_activity_price(activity: dict) -> float:
    """Calculates the activity price if applicable."""
    amount = get_activity_amount_value(activity)
    quantity = activity.get("fill_quantity", activity.get("quantity", 0))

    return (
        round(float(amount) / float(quantity), 2)
        if activity["object"] == "order" and quantity and amount
        else 0
    )


def get_activity_currency(activity: dict) -> str:
    """Determines the currency for the activity."""
    if currency := activity.get("currency"):
        return currency.upper()

    if activity.get("object") == "order" and "limit_price" in activity:
        return activity["limit_price"]["currency"].upper()

    if "account_currency" in activity:
        return activity["account_currency"].upper()

    return activity.get("market_value", {}).get("currency", "None")


def clean_fetch_activities_data(
    activities: list,
) -> tuple[list[ActivityCreate], list[SecurityCreate]]:

    activity_objects = []
    security_objects = {}

    for activity in activities:
        action_data = {
            "object": activity.get("object"),
            "orderType": activity.get("order_type"),
            "autoOrderType": activity.get("auto_order_type"),
        }

        activity_obj = ActivityCreate(
            id=activity["id"],
            currency=get_activity_currency(activity),
            type=WSIMPLE_ACTIVITY_TYPE_DICT.get(activity["object"], "Unknown"),
            sub_type=activity.get("order_sub_type"),
            action=get_activity_action(action_data),
            stop_price=activity.get("stop_price", 0),
            price=get_activity_price(activity),
            quantity=activity.get("quantity", 0),
            symbol=activity.get("symbol"),
            amount=get_activity_amount_value(activity),
            commission=activity.get("filledTotalTransactionFee", {}).get("amount", 0),
            option_multiplier=activity.get("option_multiplier"),
            market_currency=activity.get("market_currency")
            or activity.get("net_cash", {}).get("currency"),
            status=activity.get("status"),
            cancelled_at=activity.get("cancelled_at"),
            rejected_at=activity.get("rejected_at"),
            submitted_at=activity.get("submitted_at"),
            filled_at=activity.get("filled_at"),
            account_id=activity.get(
                "destination_account_id", activity.get("account_id")
            ),
            security_id=activity.get("security_id"),
        )
        activity_objects.append(activity_obj)

        # Avoid duplicate securities
        if (
            activity.get("security_id")
            and activity["security_id"] not in security_objects
        ):
            security_obj = SecurityCreate(
                id=activity["security_id"],
                symbol=activity.get("symbol"),
                name=activity.get("security_name"),
                currency=get_activity_currency(activity),
            )
            security_objects[activity["security_id"]] = security_obj

    return activity_objects, list(security_objects.values())
