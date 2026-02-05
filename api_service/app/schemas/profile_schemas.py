from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models import UserRole


class ProfileBase(SQLModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    ci: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    age: Optional[int] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
