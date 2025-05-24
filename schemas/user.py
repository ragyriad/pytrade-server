from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: Optional[str] = "user"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
