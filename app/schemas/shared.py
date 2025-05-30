from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional, Any
from app.utils.utils import to_utc_datetime


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


class SyncResponse(BaseModel):
    count: int
    message: Optional[str] = None


class UTCBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    @field_validator("*", mode="before")
    @classmethod
    def _convert_all_datetimes(cls, v: Any, info) -> Any:
        if (
            hasattr(info, "field")
            and info.field.annotation is datetime
            and v is not None
        ):
            return to_utc_datetime(v)
        return v
