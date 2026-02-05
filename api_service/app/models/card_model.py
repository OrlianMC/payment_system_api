from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .user_model import User
    from .payment_model import Payment


class CardBrand(str, Enum):
    visa = "visa"
    mastercard = "mastercard"
    amex = "amex"
    discover = "discover"


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    card_holder_name: str
    brand: CardBrand = Field(default=CardBrand.visa)

    last_four: str
    masked_number: str

    expiration_month: int
    expiration_year: int

    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="cards")
    payments: List["Payment"] = Relationship(back_populates="card")
