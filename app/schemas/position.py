from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, ConfigDict, EmailStr
from enum import Enum

from .account import AccountResponse
from .security import SecurityResponse


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
