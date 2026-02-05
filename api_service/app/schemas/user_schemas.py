from datetime import datetime
from sqlmodel import SQLModel
from app.models import UserRole


class UserBase(SQLModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserPasswordReset(SQLModel):
    new_password: str
    current_password: str


class UserUpdate(UserCreate):
    pass


class UserLogin(UserBase):
    email: str
    password: str


class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime


# ---------- TOKEN ----------


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
