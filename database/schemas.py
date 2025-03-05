from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, field_validator, ConfigDict, EmailStr
from enum import Enum


# ---------------------------
# Shared Schemas
# ---------------------------


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


# Base schema with common attributes
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: Optional[str] = "user"


# Schema for creating a new user (password required)
class UserCreate(UserBase):
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str


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


class ActivityUpdate(BaseModel):
    status: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    amount: Optional[float] = None
    commission: Optional[float] = None
    market_currency: Optional[str] = None


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


from pydantic import BaseModel, UUID4, condecimal
from typing import Optional, List
from datetime import datetime


# ✅ User Response Model
class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True


# ✅ Account Response Model
class AccountResponse(BaseModel):
    account_number: str
    type: str
    current_balance: condecimal(max_digits=20, decimal_places=2)
    net_deposits: condecimal(max_digits=20, decimal_places=2)
    currency: str
    status: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime
    last_synced: datetime
    linked_account_id: Optional[str]
    account_broker_id: Optional[str]

    class Config:
        from_attributes = True


# ✅ Deposit Response Model
class DepositResponse(BaseModel):
    id: str
    bank_account_id: Optional[str]
    status: Optional[str]
    currency: Optional[str]
    amount: condecimal(max_digits=10, decimal_places=2)
    cancelled_at: Optional[datetime]
    rejected_at: Optional[datetime]
    accepted_at: Optional[datetime]
    created_at: datetime
    last_synced: Optional[datetime]
    account_id: Optional[str]

    class Config:
        from_attributes = True


# ✅ Activity Response Model
class ActivityResponse(BaseModel):
    id: str
    currency: Optional[str]
    type: str
    sub_type: Optional[str]
    action: Optional[str]
    stop_price: Optional[condecimal(max_digits=10, decimal_places=2)]
    price: condecimal(max_digits=10, decimal_places=2)
    quantity: condecimal(max_digits=10, decimal_places=2)
    amount: Optional[condecimal(max_digits=10, decimal_places=2)]
    commission: condecimal(max_digits=10, decimal_places=2)
    option_multiplier: Optional[str]
    symbol: Optional[str]
    market_currency: Optional[str]
    status: Optional[str]
    cancelled_at: Optional[datetime]
    rejected_at: Optional[datetime]
    submitted_at: Optional[datetime]
    filled_at: Optional[datetime]
    created_at: datetime
    last_updated: datetime
    last_synced: datetime
    security_id: Optional[str]
    account_id: str

    class Config:
        from_attributes = True


# ✅ Position Response Model
class PositionResponse(BaseModel):
    id: UUID4
    quantity: condecimal(max_digits=20, decimal_places=2)
    amount: condecimal(max_digits=20, decimal_places=2)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    security_id: Optional[str]
    account_id: Optional[str]

    class Config:
        from_attributes = True


# ✅ Broker Response Model
class BrokerResponse(BaseModel):
    id: UUID4
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ✅ Security Response Model
class SecurityResponse(BaseModel):
    id: str
    symbol: str
    name: Optional[str]
    description: Optional[str]
    type: Optional[str]
    currency: Optional[str]
    status: Optional[str]
    exchange: Optional[str]
    option_details: Optional[str]
    order_subtypes: Optional[str]
    trade_eligible: bool
    options_eligible: bool
    buyable: bool
    sellable: bool
    active_date: Optional[datetime]
    created_at: datetime
    last_synced: datetime
    security_id: Optional[str]

    class Config:
        from_attributes = True
