from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .card_model import Card
    from .user_model import User


class PaymentStatus(str, Enum):
    approved = "approved"
    rejected = "rejected"
    pending = "pending"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
    card_id: int = Field(foreign_key="cards.id")

    amount: float
    currency: str = "USD"

    status: PaymentStatus = Field(default=PaymentStatus.pending)
    status_reason: Optional[str] = None

    processor_reference: Optional[str] = None
    idempotency_key: Optional[str] = Field(default=None, index=True)

    processed_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    user: Optional["User"] = Relationship(back_populates="payments")
    card: Optional["Card"] = Relationship(back_populates="payments")
