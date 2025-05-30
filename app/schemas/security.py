from datetime import datetime
from typing import Optional
from app.schemas.shared import CurrencyCode, UTCBase


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

    class Config:
        from_attributes = True
