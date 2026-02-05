from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .card_model import Card
    from .payment_model import Payment
    from .profile_model import Profile


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.user)
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    cards: List["Card"] = Relationship(back_populates="user")
    payments: List["Payment"] = Relationship(back_populates="user")
    profile: Optional["Profile"] = Relationship(back_populates="user")
