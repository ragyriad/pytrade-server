from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, field_validator, ConfigDict
from enum import Enum


# ---------------------------
# Shared Schemas
# ---------------------------
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


# ---------------------------
# Broker Schemas
# ---------------------------
class BrokerBase(BaseModel):
    name: str = Field(..., example="Wealthsimple")


class BrokerCreate(BrokerBase):
    pass


class BrokerResponse(BrokerBase):
    id: UUID4
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Account Schemas
# ---------------------------
class AccountBase(BaseModel):
    type: AccountType
    currency: CurrencyCode
    status: str = Field(..., example="ACTIVE")
    is_primary: bool = False


class AccountCreate(AccountBase):
    current_balance: float = Field(0.0, ge=0)
    net_deposits: float = Field(0.0, ge=0)

    @field_validator("type")
    @classmethod
    def validate_account_type(cls, v: AccountType) -> AccountType:
        if not isinstance(v, AccountType):
            raise ValueError("Invalid account type")
        return v


class AccountUpdate(AccountBase):
    current_balance: Optional[float] = None
    net_deposits: Optional[float] = None


class AccountResponse(AccountBase):
    account_number: str
    linked_account: Optional[AccountResponse] = None  # Self reference
    account_broker: Optional[BrokerResponse] = None
    created_at: datetime
    updated_at: datetime
    last_synced: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Security Schemas
# ---------------------------
class SecurityBase(BaseModel):
    symbol: str = Field(..., max_length=20)
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = Field(None, example="STOCK")
    currency: Optional[CurrencyCode] = None
    status: Optional[str] = Field(None, example="ACTIVE")


class SecurityCreate(SecurityBase):
    exchange: Optional[str] = None
    option_details: Optional[str] = None
    order_subtypes: Optional[str] = None
    trade_eligible: bool = False
    options_eligible: bool = False


class SecurityResponse(SecurityBase):
    id: str
    accounts: List[AccountResponse] = []
    created_at: datetime
    last_synced: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Position Schemas
# ---------------------------
class PositionBase(BaseModel):
    quantity: float = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    is_active: bool


class PositionCreate(PositionBase):
    security_id: str
    account_number: str


class PositionResponse(PositionBase):
    id: UUID4
    security: SecurityResponse
    account: AccountResponse
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Activity Schemas
# ---------------------------
class TotalAmountResponse(BaseModel):
    totalAmount: float


class TradesCountResponse(BaseModel):
    tradesCount: int


class ActivityType(str, Enum):
    TRADE = "TRADE"
    DIVIDEND = "DIVIDEND"
    TRANSFER = "TRANSFER"
    DEPOSIT = "DEPOSIT"


class ActivityBase(BaseModel):
    type: ActivityType
    currency: CurrencyCode
    amount: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    status: str = Field(..., example="FILLED")


class ActivityCreate(ActivityBase):
    security_id: Optional[str] = None
    account_number: str


class ActivityResponse(ActivityBase):
    id: str
    security: Optional[SecurityResponse] = None
    account: AccountResponse
    created_at: datetime
    last_updated: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Deposit Schemas
# ---------------------------
class DepositStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DepositBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: CurrencyCode
    status: DepositStatus


class DepositCreate(DepositBase):
    account_number: str


class DepositResponse(DepositBase):
    id: str
    account: AccountResponse
    created_at: datetime
    last_synced: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Security Group Schemas
# ---------------------------
class SecurityGroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class SecurityGroupResponse(SecurityGroupBase):
    id: str
    securities: List[SecurityResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Resolve forward references at module level
AccountResponse.model_rebuild()
SecurityResponse.model_rebuild()
