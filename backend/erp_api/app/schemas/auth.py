"""Auth-related Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Role = Role.VIEWER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: Role
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenPayload(BaseModel):
    sub: str  # user id
    email: str
    role: str
    exp: Optional[datetime] = None
    type: str = "access"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse
