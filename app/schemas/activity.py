from __future__ import annotations
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from enum import Enum

from .shared import CurrencyCode, UTCBase


class TotalAmountResponse(BaseModel):
    totalAmount: float


class TradesCountResponse(BaseModel):
    tradesCount: int


class ActivityType(str, Enum):
    CONVERT_FUNDS = "Convert Funds"
    DIVIDEND = "Dividend"
    ORDER = "Order"
    DEPOSIT = "Deposit"
    CORPORATE_ACTION = "Corporate Action"
    FEES_AND_REBATES = "Fees and Rebates"
    OPTION = "Option"
    OTHER = "Other"
    NONE = None


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
