import calendar
import re
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import HTTPException
	from sqlalchemy.ext.asyncio import AsyncSession
import functools
import asyncio
from qtrade import Questrade

from database.models import Account, Activity, Security
from repositories.base_repository import BaseRepository
from repositories.account_respository import AccountRepository
from schemas.settings import settings
from utils.utils import open_file
from data.constants import (
    SECURITY_UPDATE_FIELDS,
    SECURITY_UNIQUE_FIELD,
    ACTIVITY_UNIQUE_FIELD,
    ACTIVITY_UPDATE_FIELDS,
    QUESTRADE_ACTIVITY_TYPE_DICT,
)


base_path = Path(__file__).parent.parent
file_path = (base_path / "brokers/questrade.yaml").resolve()


class QuestradeService:
    def __init__(self, account_repo: AccountRepository = None, logger=None):
        self.logger = logger
        self._client = None
        self.account_repo = account_repo

    def refresh_token_if_unauthorized(fn):
        @functools.wraps(fn)
        async def wrapper(self, *args, **kwargs):
            print("###IN REFRESH TOKEN DECORATOR###")
            if self._client is None:
                print("Client not initialized, authenticating...")
                # If authenticate is async, use await. If not, just call it.
                result = self.authenticate()
                if asyncio.iscoroutine(result):
                    await result

            try:
                return await fn(self, *args, **kwargs)
            except Exception as e:
                err_message = str(e).lower()
                print(f"Caught error: {err_message}")

                # Check for unauthorized or expired token errors - USE LOWERCASE MATCHES
                if (
                    "unauthorized" in err_message
                    or "401" in err_message
                    or (
                        "token" in err_message
                        and ("expired" in err_message or "invalid" in err_message)
                    )
                ):
                    print("Token expired or unauthorized, trying to refresh tokens...")
                    try:
                        # If refresh_access_token is async, use await
                        result = self._client.refresh_access_token(
                            from_yaml=True, yaml_path=file_path
                        )
                        if asyncio.iscoroutine(result):
                            await result
                        print("Refresh token succeeded.")
                    except Exception as refresh_err:
                        refresh_msg = str(refresh_err).lower()
                        print(f"Refresh token failed: {refresh_err}")

                        if "400" in refresh_msg or "bad request" in refresh_msg:
                            print(
                                "Refresh token invalid/outdated, running full authentication."
                            )
                            result = self.authenticate()
                            if asyncio.iscoroutine(result):
                                await result
                        else:
                            raise refresh_err

                    # Retry original function
                    return await fn(self, *args, **kwargs)
                else:
                    print(f"Not an auth error, re-raising: {err_message}")
                    raise

        return wrapper

    def authenticate(self):
        tokens = open_file(file_path)
        print("Tokens loaded from file:", tokens)
        try:
            qt = Questrade(access_code=tokens.get("access_code", None))
            self._client = qt
            print("Successfully authenticated using existing tokens.")
            return qt
        except Exception as e:
            print("Existing token failed, trying to refresh or regenerate token...", e)

        # Scenario 2: API unauthorized AND you have an access_code (grant code) to generate NEW tokens
        if "access_code" in tokens and tokens["access_code"]:
            try:
                print("Using access_code to generate new tokens.")
                qt = Questrade(access_code=tokens["access_code"])
                qt._get_access_token(save_yaml=True, yaml_path=file_path)
                print("Generated and saved new token set using access_code.")
                return qt
            except Exception as e:
                print("Failed to generate new token using access_code:", e)

        # Scenario 3: Try to refresh with refresh token
        if "refresh_token" in tokens and tokens["refresh_token"]:
            try:
                print("Using refresh_token to refresh tokens.")
                qt = Questrade(token_yaml=file_path)
                qt.refresh_access_token(from_yaml=True, yaml_path=file_path)
                print("Refreshed and saved new token set using refresh_token.")
                return qt
            except Exception as e:
                print("Failed to refresh token using refresh_token:", e)

        # If all methods fail
        raise Exception("No valid authentication method found for Questrade.")

    def get_activity_action(self, activity):
        if activity["type"] == "Trades":
            value = float(activity["netAmount"])
            return "Sell" if value > 0 else "Buy" if value < 0 else None

    @refresh_token_if_unauthorized
    async def sync_accounts(self, db: AsyncSession):
        try:
            self.authenticate()
            fetched_accounts = self._client.get_accounts()
            print("Fetched ACCOUNTS -> ", fetched_accounts)
            print(
                "Type of save_accounts result:", type(self.account_repo.save_accounts)
            )
            saved_accounts = self.account_repo.save_accounts(db, fetched_accounts)
            print("Saved ACCOUNTS -> ", saved_accounts)

            return {"count": len(saved_accounts), "saved_accounts": saved_accounts}

        except Exception as e:
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))

    @refresh_token_if_unauthorized
    async def sync_activities(self, db: AsyncSession):
        """Fetch and sync Questrade activities."""
        try:
            self.authenticate()
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

                        response = self._client.account_activities(
                            account_number, startTime=start_time, endTime=end_time
                        )
                        activities = response["activities"]

                        print(f"Found {len(activities)} activities")
                        options_pattern = r"^.*\d{1,2}[A-Za-z]{3}\d{2}P\d{1,}\.\d{2}$"

                        for activity in activities:
                            is_option = bool(
                                re.match(options_pattern, activity["symbol"])
                            )
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
                                    action=self.get_activity_action(activity),
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

    @refresh_token_if_unauthorized
    async def sync_questrade_data(self, db: AsyncSession):
        try:
            account_sync_result = self.sync_accounts(db)
            activity_sync_result = self.sync_activities(db)

            return {
                "accounts_synced": account_sync_result["count"],
                "activities_synced": activity_sync_result["activity_count"],
            }

        except Exception as e:
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
