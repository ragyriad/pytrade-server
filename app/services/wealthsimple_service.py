import asyncio
from fastapi import HTTPException
from typing import Optional

from ws_api import WealthsimpleAPI
from app.utils.redis import get_from_redis, set_to_redis, delete_from_redis
from app.schemas.schemas import SecurityCreate
from app.database.models import Activity, Security
from app.repositories.base_repository import BaseRepository
from app.services.session_manager import load_session, persist_session
from config.settings import (
    SECURITY_UNIQUE_FIELD,
    SECURITY_UPDATE_FIELDS,
    ACTIVITY_UPDATE_FIELDS,
    ACTIVITY_UNIQUE_FIELD,
    WEALTHSIMPLE_ACTIVITIES_TYPES,
    WSIMPLE_ACTIVITY_TYPE_DICT,
)


class WealthsimpleService:
    def __init__(self):
        self.ws: Optional[WealthsimpleAPI] = None

    async def get_client(self) -> WealthsimpleAPI:
        if not self.ws:
            session = load_session()
            if not session:

                raise RuntimeError("Session not found. Please log in.")
            self.ws = WealthsimpleAPI.from_token(
                session, persist_session_fct=persist_session
            )
        return self.ws

    async def login(self, email: str, password: str, otp: Optional[str] = None) -> str:
        WealthsimpleAPI.login(
            username=email,
            password=password,
            otp_answer=otp,
            persist_session_fct=persist_session,
        )

        session = load_session()
        if not session:
            raise RuntimeError("Failed to load saved session.")

        self.ws = WealthsimpleAPI.from_token(
            session, persist_session_fct=persist_session
        )
        print("THIS IS IT!")
        token_data = {
            "access_token": getattr(session, "access_token", None),
            "refresh_token": getattr(session, "refresh_token", None),
            "session_id": getattr(session, "session_id", None),
        }
        return token_data

    async def refresh_tokens(self):
        self.ws = await self.get_client()
        self.ws.refresh_token()
        persist_session(self.ws.session.serialize())

    def update_env_file(self, key: str, value: str):
        with open(".env", "r") as file:
            lines = file.readlines()
        with open(".env", "w") as file:
            for line in lines:
                if line.startswith(key):
                    file.write(f"{key}={value}\n")
                else:
                    file.write(line)

    async def sync_securities(self):
        """Fetch and sync securities data."""
        if not self.ws:
            raise HTTPException(
                status_code=401, detail="Unauthorized. No session found."
            )
        securities = await self.ws.get_securities()
        return securities

    async def sync_accounts(self):
        """Fetch and sync account data."""
        if not self.ws:
            raise HTTPException(
                status_code=401, detail="Unauthorized. No session found."
            )
        accounts = await self.ws.get_accounts()
        return accounts

    async def sync_positions(self):
        """Fetch and sync positions data."""
        if not self.ws:
            raise HTTPException(
                status_code=401, detail="Unauthorized. No session found."
            )
        positions = await self.ws.get_positions()
        return positions

    async def sync_wealthsimple_data(self, db):
        """Sync all data from Wealthsimple (securities, activities, etc.)"""
        await self.initiate_connection()
        securities_data = await self.ws.get_securities()
        securities = [SecurityCreate(**s) for s in securities_data]
        security_repo = BaseRepository(db, Security)
        activity_repo = BaseRepository(db, Activity)
        security_repo.safe_bulk_create(
            securities, SECURITY_UNIQUE_FIELD, SECURITY_UPDATE_FIELDS
        )

        activities_data = await self.fetch_activities_async()
        activities, securities = self.clean_fetch_activities_data(activities_data)

        security_repo.safe_bulk_create(
            securities, SECURITY_UNIQUE_FIELD, SECURITY_UPDATE_FIELDS
        )
        count = activity_repo.safe_bulk_create(
            activities, ACTIVITY_UNIQUE_FIELD, ACTIVITY_UPDATE_FIELDS
        )

        return count, "Wealthsimple data synchronized successfully"

    async def fetch_activities_async(self):
        """Fetches all Wealthsimple activities asynchronously"""
        tasks = []
        for activity_type in WEALTHSIMPLE_ACTIVITIES_TYPES:
            if activity_type != "all":
                tasks.append(
                    self.ws.get_activities({"limit": 99, "type": activity_type})
                )
        return await asyncio.gather(*tasks)

    def clean_fetch_activities_data(self, activities):
        """Clean and process fetched activities data."""
        activitiesObjList = []
        securitiesObjList = []

        for activity in activities:
            actionFnData = {
                "object": activity["object"],
                "orderType": (
                    activity["order_type"] if "order_type" in activity else None
                ),
                "autoOrderType": (
                    activity["auto_order_type"]
                    if "auto_order_type" in activity
                    else None
                ),
            }
            amountValue = self.get_activity_amount_value(activity)
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
                currency=self.get_activity_currency(activity),
                type=WSIMPLE_ACTIVITY_TYPE_DICT[activity["object"]],
                sub_type=(
                    activity["order_sub_type"] if "order_sub_type" in activity else None
                ),
                action=self.get_activity_action(actionFnData),
                stop_price=activity["stop_price"] if "stop_price" in activity else 0,
                price=self.get_activity_price(activity),
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
                rejected_at=(
                    activity["rejected_at"] if "rejected_at" in activity else None
                ),
                submitted_at=(
                    activity["submitted_at"] if "submitted_at" in activity else None
                ),
                filled_at=activity["filled_at"] if "filled_at" in activity else None,
                account_id=accountIdVal,
                security_id=(
                    activity["security_id"] if "security_id" in activity else None
                ),
            )
            activitiesObjList.append(activityObj)
            if "security_id" in activity and activity["security_id"] not in (
                getattr(security, "id") for security in securitiesObjList
            ):
                securityObj = Security(
                    id=activity["security_id"],
                    symbol=symbolVal,
                    name=activity["security_name"],
                    currency=self.get_activity_currency(activity),
                )
                securitiesObjList.append(securityObj)
        return activitiesObjList, securitiesObjList

    def get_activity_action(self, action_dict: dict) -> str:
        """Determines the activity action based on order type and object type."""
        object_type, order_type, auto_order_type = (
            action_dict.get("object"),
            action_dict.get("orderType"),
            action_dict.get("autoOrderType"),
        )

        if object_type == "dividend":
            return (
                "DRIP"
                if auto_order_type == "dividend_reinvestment"
                else "Cash Dividend"
            )

        return order_type.split("_")[0].capitalize() if order_type else None

    def get_activity_amount_value(self, data: dict) -> float:
        """Extracts the correct amount value based on the activity type."""
        if "filled_net_value" in data:
            return data["filled_net_value"]
        if data.get("object") == "dividend":
            return data["net_cash"]["amount"]
        return None

    def get_activity_price(self, activity: dict) -> float:
        """Calculates the activity price if applicable."""
        amount = self.get_activity_amount_value(activity)
        quantity = activity.get("fill_quantity", activity.get("quantity", 0))

        return (
            round(float(amount) / float(quantity), 2)
            if activity["object"] == "order" and quantity and amount
            else 0
        )

    def get_activity_currency(self, activity: dict) -> str:
        """Determines the currency for the activity."""
        if currency := activity.get("currency"):
            return currency.upper()

        if activity.get("object") == "order" and "limit_price" in activity:
            return activity["limit_price"]["currency"].upper()

        if "account_currency" in activity:
            return activity["account_currency"].upper()

        return activity.get("market_value", {}).get("currency", "None")


async def get_ws_service() -> WealthsimpleService:
    service = WealthsimpleService()
    await service.get_client()
    return service
