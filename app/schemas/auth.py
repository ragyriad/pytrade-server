from pydantic import BaseModel, EmailStr
from typing import Optional


class BrokerLoginRequest(BaseModel):
    email: EmailStr
    password: str
    otp: Optional[str] = None


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    session_id: str


class BrokerLoginResponse(BaseModel):
    message: str
    session_tokens: TokenData
