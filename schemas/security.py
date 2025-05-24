from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, field_validator, ConfigDict, EmailStr
from enum import Enum


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
