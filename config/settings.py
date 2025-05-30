from pydantic_settings import BaseSettings
from typing import List, Dict
from zoneinfo import ZoneInfo


class Settings(BaseSettings):
    DATABASE_URL: str
    WSIMPLE_EMAIL: str

    DEBUG: bool = True
    MAX_RETRIES: int = 2
    QUESTRADE_TIMEZONE: ZoneInfo = ZoneInfo("America/Toronto")

    DB_BROKERS_SEED: List[str] = ["Questrade", "Wealthsimple", "Interactive Brokers"]

    SECURITY_UNIQUE_FIELD: List[str] = ["id"]
    DEPOSIT_UNIQUE_FIELD: List[str] = ["id"]

    DEPOSIT_UPDATE_FIELDS: List[str] = [
        "bank_account_id",
        "status",
        "currency",
        "amount",
        "cancelled_at",
        "rejected_at",
        "accepted_at",
        "created_at",
        "last_synced",
        "account_id",
    ]

    QUESTRADE_ACTIVITY_TYPE_DICT: Dict[str, str] = {
        "FX conversion": "Convert Funds",
        "Dividends": "Dividend",
        "Trades": "Order",
        "Deposits": "Deposit",
        "Corporate actions": "Corporate Action",
        "Order": "Order",
        "Fees and rebates": "Fees and Rebates",
        "Option": "Option",
        "Other": "Other",
    }

    WSIMPLE_ACTIVITY_TYPE_DICT: Dict[str, str] = {
        "institutional_transfer": "Institutional Transfer",
        "order": "Order",
        "convert_funds": "Convert Funds",
        "dividend": "Dividend",
        "internal_transfer": "Internal Transfer",
        "fpl_securities_lending": "Securities Lending",
        "fpl_interest_earnings": "Interest Earnings",
    }

    SECURITYGROUP_UNIQUE_FIELD: List[str] = ["id"]
    ACCOUNT_UNIQUE_FIELD: List[str] = ["account_number"]
    ACTIVITY_UNIQUE_FIELD: List[str] = ["id"]
    ACCOUNTPOSITION_UNIQUE_FIELD: List[str] = ["security_id", "account_id"]

    SECURITY_UPDATE_FIELDS: List[str] = [
        "name",
        "description",
        "type",
        "currency",
        "status",
        "exchange",
        "option_details",
        "order_subtypes",
        "trade_eligible",
        "options_eligible",
        "buyable",
        "sellable",
        "active_date",
        "last_synced",
    ]

    ACCOUNT_UPDATE_FIELDS: List[str] = [
        "type",
        "current_balance",
        "net_deposits",
        "currency",
        "status",
        "updated_at",
        "last_synced",
    ]

    ACTIVITY_UPDATE_FIELDS: List[str] = [
        "currency",
        "type",
        "sub_type",
        "action",
        "stop_price",
        "price",
        "quantity",
        "amount",
        "commission",
        "option_multiplier",
        "security_id",
        "symbol",
        "market_currency",
        "status",
        "cancelled_at",
        "rejected_at",
        "submitted_at",
        "filled_at",
        "created_at",
        "last_updated",
        "last_synced",
    ]

    SECURITYGROUP_UPDATE_FIELDS: List[str] = ["name", "description"]

    ACCOUNTPOSITION_UPDATE_FIELDS: List[str] = [
        "quantity",
        "amount",
        "is_active",
        "security_id",
        "account_id",
    ]

    WEALTHSIMPLE_ACTIVITIES_TYPES: List[str] = [
        "all",
        "deposit",
        "withdrawal",
        "buy",
        "sell",
        "dividend",
        "institutional_transfer",
        "internal_transfer",
        "refund",
        "referral_bonus",
        "affiliate",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
        case_sensitive = True


settings = Settings()
