from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, UUID4, ConfigDict, field_validator
from enum import Enum
from app.utils.utils import to_utc_datetime


# --------------------
# UTCBase (for all)
# --------------------
class UTCBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    @field_validator("*", mode="before")
    @classmethod
    def _convert_all_datetimes(cls, v, info):
        if v is not None and (isinstance(v, str) or isinstance(v, datetime)):
            try:
                return to_utc_datetime(v)
            except Exception:
                return v
        return v


# --------------------
# Enums
# --------------------
class MFACode(BaseModel):
    code: str


class Token(BaseModel):
    code: str


class SyncResponse(BaseModel):
    count: int
    message: Optional[str] = None


class CurrencyCode(str, Enum):
    CAD = "CAD"
    USD = "USD"
    EUR = "EUR"


class AccountType(str, Enum):
    TFSA = "TFSA"
    RRSP = "RRSP"
    PERSONAL = "PERSONAL"
    CRYPTO = "CRYPTO"
    NON_REGISTERED = "NON_REGISTERED"


class DepositStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ActivityType(str, Enum):
    TRADE = "TRADE"
    DIVIDEND = "DIVIDEND"
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"


# --------------------
# User
# --------------------
class UserBase(UTCBase):
    email: str
    is_active: bool = True
    role: str = "user"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int


# --------------------
# Broker
# --------------------
class BrokerBase(UTCBase):
    name: str


class BrokerCreate(BrokerBase):
    pass


class BrokerResponse(BrokerBase):
    id: UUID4
    created_at: datetime


# --------------------
# Account
# --------------------
class AccountBase(UTCBase):
    type: AccountType
    currency: CurrencyCode
    status: str
    is_primary: bool = False


class AccountCreate(AccountBase):
    account_number: str
    current_balance: Decimal = Field(0, ge=0)
    net_deposits: Decimal = Field(0, ge=0)
    linked_account_id: Optional[str] = None
    account_broker_id: str


class AccountUpdate(UTCBase):
    type: Optional[AccountType]
    currency: Optional[CurrencyCode]
    status: Optional[str]
    is_primary: Optional[bool]
    current_balance: Optional[Decimal]
    net_deposits: Optional[Decimal]
    linked_account_id: Optional[str]
    account_broker_id: Optional[str]


class AccountResponse(AccountCreate):
    created_at: datetime
    updated_at: datetime
    last_synced: datetime


# --------------------
# Deposit
# --------------------
class DepositBase(UTCBase):
    amount: Decimal
    currency: CurrencyCode
    status: DepositStatus


class DepositCreate(DepositBase):
    id: Optional[str] = None
    bank_account_id: Optional[str] = None
    account_id: str


class DepositUpdate(UTCBase):
    status: Optional[DepositStatus]
    cancelled_at: Optional[datetime]
    rejected_at: Optional[datetime]
    accepted_at: Optional[datetime]


class DepositResponse(DepositBase):
    id: str
    bank_account_id: Optional[str]
    cancelled_at: Optional[datetime]
    rejected_at: Optional[datetime]
    accepted_at: Optional[datetime]
    created_at: datetime
    last_synced: Optional[datetime]
    account_id: str


# --------------------
# Activity
# --------------------
class ActivityBase(UTCBase):
    type: Optional[str] = None
    currency: Optional[CurrencyCode]
    amount: Optional[Decimal] = 0.0
    quantity: Decimal
    status: Optional[str]
    sub_type: Optional[str] = None
    action: Optional[str] = None
    stop_price: Optional[Decimal] = None
    price: Decimal
    commission: Decimal
    option_multiplier: Optional[str] = None
    symbol: Optional[str] = None
    market_currency: Optional[str] = None


class ActivityCreate(ActivityBase):
    id: Optional[str] = None
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    security_id: Optional[str] = None
    account_id: str


class ActivityUpdate(UTCBase):
    status: Optional[str]
    cancelled_at: Optional[datetime]
    rejected_at: Optional[datetime]
    submitted_at: Optional[datetime]
    filled_at: Optional[datetime]
    price: Optional[Decimal]
    quantity: Optional[Decimal]
    amount: Optional[Decimal]
    commission: Optional[Decimal]
    stop_price: Optional[Decimal]


class ActivityResponse(ActivityCreate):
    created_at: datetime
    last_updated: datetime
    last_synced: datetime


# --------------------
# Position
# --------------------
class PositionBase(UTCBase):
    quantity: Decimal
    amount: Decimal
    is_active: bool


class PositionCreate(PositionBase):
    id: Optional[UUID4] = None
    security_id: Optional[str]
    account_id: Optional[str]


class PositionUpdate(UTCBase):
    quantity: Optional[Decimal]
    amount: Optional[Decimal]
    is_active: Optional[bool]


class PositionResponse(PositionCreate):
    created_at: datetime
    updated_at: datetime


# --------------------
# Security
# --------------------
class SecurityBase(UTCBase):
    symbol: str
    name: Optional[str]
    description: Optional[str]
    type: Optional[str]
    currency: Optional[CurrencyCode]
    status: Optional[str]
    exchange: Optional[str]
    option_details: Optional[str]
    order_subtypes: Optional[str]
    trade_eligible: bool = False
    options_eligible: bool = False
    buyable: bool = False
    sellable: bool = False
    active_date: Optional[datetime] = None


class SecurityCreate(SecurityBase):
    id: Optional[str] = None


class SecurityUpdate(UTCBase):
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    option_details: Optional[str]
    order_subtypes: Optional[str]
    buyable: Optional[bool]
    sellable: Optional[bool]
    active_date: Optional[datetime]


class SecurityResponse(SecurityCreate):
    created_at: datetime
    last_synced: datetime
