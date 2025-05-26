import calendar, re, traceback, uuid, time, asyncio, functools, inspect
from datetime import datetime, timezone
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from qtrade import Questrade

from app.database.models import Account, Activity, Security
from app.repositories.base_repository import BaseRepository
from app.repositories.account_respository import AccountRepository
from app.schemas.settings import settings
from app.utils.utils import (
    open_file,
    write_file,
    generate_expiry_timestamp,
    yaml_file_exists,
)
from app.data.constants import (
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

    def is_token_valid(self, expires_at: int, buffer_seconds: int = 60) -> bool:
        current_time = int(time.time())
        print(
            f"Current time: {current_time + buffer_seconds}, Expires at: {expires_at}"
        )
        return (current_time + buffer_seconds) < expires_at

    def get_new_tokens(self) -> bool:
        try:
            input_access_code = input(
                "Token refresh failed. Please enter a new access code: "
            )
            qt = Questrade(access_code=input_access_code)
            token_expiry = generate_expiry_timestamp(qt.access_token["expires_in"])
            qt.access_token["expires_at"] = token_expiry
            print("New access code tokens ->", qt.access_token)
            return qt

        except Exception as input_exc:
            print("Failed to authenticate with new access code:", input_exc)
            raise input_exc

    def refresh_token_if_unauthorized(fn):
        @functools.wraps(fn)
        async def async_wrapper(self, *args, **kwargs):
            if self._client is None:
                auth_result = self.authenticate()
                if asyncio.iscoroutine(auth_result):
                    await auth_result

            try:
                return await fn(self, *args, **kwargs)
            except Exception as e:
                err_message = str(e).lower()
                auth_error = (
                    "unauthorized" in err_message
                    or "401" in err_message
                    or (
                        "token" in err_message
                        and ("expired" in err_message or "invalid" in err_message)
                    )
                )
                if not auth_error:
                    raise
                try:
                    refresh_result = self._client.refresh_access_token(
                        from_yaml=True, yaml_path=file_path
                    )
                    if asyncio.iscoroutine(refresh_result):
                        await refresh_result
                except Exception as refresh_err:
                    refresh_msg = str(refresh_err).lower()
                    if "400" in refresh_msg or "bad request" in refresh_msg:
                        reauth_result = self.authenticate()
                        if asyncio.iscoroutine(reauth_result):
                            await reauth_result
                    else:
                        raise
                # Retry
                return await fn(self, *args, **kwargs)

        @functools.wraps(fn)
        def sync_wrapper(self, *args, **kwargs):
            if self._client is None:
                self.authenticate()

            try:
                return fn(self, *args, **kwargs)
            except Exception as e:
                err_message = str(e).lower()
                auth_error = (
                    "unauthorized" in err_message
                    or "401" in err_message
                    or (
                        "token" in err_message
                        and ("expired" in err_message or "invalid" in err_message)
                    )
                )
                if not auth_error:
                    raise

                # Try refresh
                try:
                    self._client.refresh_access_token(
                        from_yaml=True, yaml_path=file_path
                    )
                except Exception as refresh_err:
                    refresh_msg = str(refresh_err).lower()
                    if "400" in refresh_msg or "bad request" in refresh_msg:
                        self.authenticate()
                    else:
                        raise
                # Retry
                return fn(self, *args, **kwargs)

        if inspect.iscoroutinefunction(fn):
            return async_wrapper
        else:
            return sync_wrapper

    def authenticate(self):
        tokens = open_file(file_path)
        print("Tokens loaded from file:", tokens)
        try:
            if yaml_file_exists(file_path):
                print("YAML file exists, loading tokens from it.")
                yaml_token = open_file(file_path)
                print("YAML token loaded:", yaml_token)
                qt = Questrade(token_yaml=file_path)
                if self.is_token_valid(
                    qt.access_token.get("expires_at", 0), buffer_seconds=60
                ):
                    print("Yaml Access token is valid, using existing client.")

                    qt.access_token = yaml_token
                    self._client = qt
                    return True
                else:
                    print("Yaml Access token is invalid, refreshing...")
                    try:
                        qt.refresh_access_token(from_yaml=True, yaml_path=file_path)
                    except Exception as refresh_error:
                        print(f"Token refresh failed: {refresh_error}")
                        print("Attempting to re-authenticate with new access code...")
                        qt = self.get_new_tokens()
                    self._client = qt
                    write_file(file_path, qt.access_token)
                    print("Refreshed access token and updated client.", qt.access_token)
                    return True
            else:
                qt = self.get_new_tokens()
                self._client = qt
                write_file(file_path, qt.access_token)
                print("Successfully authenticated with new access code.")

        except Exception as e:
            raise RuntimeError("Authentication failed") from e

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
            import inspect

            print(
                "Is save_accounts coroutine:",
                inspect.iscoroutinefunction(self.account_repo.save_accounts),
            )
            saved_accounts = await self.account_repo.save_accounts(
                db, fetched_accounts, broker="Questrade"
            )
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
