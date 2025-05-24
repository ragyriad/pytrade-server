from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, ConfigDict, EmailStr
from enum import Enum

from .shared import CurrencyCode
from .account import AccountResponse
from .security import SecurityResponse


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
