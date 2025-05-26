from pydantic import BaseModel
from enum import Enum
from typing import Optional


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
