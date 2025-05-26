from typing import List, Optional
from fastapi import Depends
from ..data.constants import WSIMPLE_ACTIVITY_TYPE_DICT
from database.models import Activity, Security
from schemas.schemas import TotalAmountResponse, TradesCountResponse, ActivityResponse
from fastapi import APIRouter
from sqlalchemy.orm import Session
from database.connection import get_db

router = APIRouter()


async def get_trades_count(self) -> int:
    activities = await self.activity_repo.find_by_type("Trades")
    return len(activities)


async def refresh_activities(self, source_id: str) -> List[ActivityResponse]:
    new_activities = await self.activity_repo.regenerate_from_source(source_id).__dict__
    return [ActivityResponse.model_validate(a) for a in new_activities]


async def get_activity_action(action_dict: dict):
    obj, order_type, auto_order_type = action_dict.values()
    if obj == "dividend":
        return "DRIP" if auto_order_type == "dividend_reinvestment" else "Cash Dividend"
    return order_type.split("_")[0].capitalize() if order_type else None


async def set_activity_amount_value(data: dict):
    if "filled_net_value" in data:
        return data["filled_net_value"]
    if data["object"] == "dividend":
        return data["net_cash"]["amount"]
    return None


async def set_activity_price(activity: dict):
    amount = set_activity_amount_value(activity)
    if activity.get("object") == "order" and amount:
        quantity = activity.get("fill_quantity", activity.get("quantity", 0))
        return round(float(amount) / float(quantity), 2) if quantity else 0
    return 0


async def set_activity_currency(activity: dict):
    if currency := activity.get("currency"):
        return currency.upper()
    if activity.get("object") == "order" and "limit_price" in activity:
        return activity["limit_price"]["currency"].upper()
    if currency := activity.get("account_currency"):
        return currency.upper()
    if activity.get("object") == "dividend" and "market_value" in activity:
        return activity["market_value"]["currency"]
    return "None"


async def clean_fetch_activities_data(activities):
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
        amountValue = set_activity_amount_value(activity)
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
            currency=set_activity_currency(activity),
            type=WSIMPLE_ACTIVITY_TYPE_DICT[activity["object"]],
            sub_type=(
                activity["order_sub_type"] if "order_sub_type" in activity else None
            ),
            action=get_activity_action(actionFnData),
            stop_price=activity["stop_price"] if "stop_price" in activity else 0,
            price=set_activity_price(activity),
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
                currency=set_activity_currency(activity),
            )
            securitiesObjList.append(securityObj)
    return activitiesObjList, securitiesObjList


def get_total_amount(db: Session, query, field: str) -> float:
    """Helper function to calculate total absolute amount from a database query."""
    amount_list = [abs(float(getattr(item, field))) for item in query]
    return round(sum(amount_list), 2)


@router.get("/account/dividends", response_model=TotalAmountResponse)
def get_account_dividends(db: Session = Depends(get_db)):
    """Returns total dividends amount."""
    query = db.query(Activity).filter(Activity.type == "Dividends").all()
    total_amount = get_total_amount(db, query, "netAmount")
    return {"totalAmount": total_amount}


@router.get("/account/commissions", response_model=TotalAmountResponse)
def get_account_commissions(db: Session = Depends(get_db)):
    """Returns total commission amount."""
    query = db.query(Activity).filter(Activity.commission < 0).all()
    total_amount = get_total_amount(db, query, "commission")
    return {"totalAmount": total_amount}


@router.get("/account/trades/count", response_model=TradesCountResponse)
def get_account_trades_count(db: Session = Depends(get_db)):
    """Returns the count of trading activities."""
    trade_count = db.query(Activity).filter(Activity.type == "Trades").count()
    return {"tradesCount": trade_count}
