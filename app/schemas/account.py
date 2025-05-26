from pydantic import BaseModel, Field, ConfigDict, condecimal
from typing import Optional
from datetime import datetime
from app.schemas.shared import CurrencyCode


class AccountBase(BaseModel):
    type: str
    currency: CurrencyCode
    status: str = Field(..., example="ACTIVE")
    is_primary: bool = False


class AccountCreate(AccountBase):
    current_balance: float = Field(0.0, ge=0)
    net_deposits: float = Field(0.0, ge=0)


class AccountResponse(AccountBase):
    account_number: str
    linked_account_id: Optional[str] = None
    account_broker_id: Optional[str] = None
    current_balance: condecimal(max_digits=20, decimal_places=2)
    net_deposits: condecimal(max_digits=20, decimal_places=2)
    created_at: datetime
    updated_at: datetime
    last_synced: datetime

    model_config = ConfigDict(from_attributes=True)
