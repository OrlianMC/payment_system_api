from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models import PaymentStatus


class PaymentCreate(SQLModel):
    user_id: int
    card_id: int
    amount: float
    currency: str = "USD"
    idempotency_key: str


class PaymentRead(SQLModel):
    id: int
    user_id: int
    card_id: int

    amount: float
    currency: str

    status: PaymentStatus
    status_reason: Optional[str]

    processor_reference: Optional[str]
    idempotency_key: Optional[str]

    processed_at: Optional[datetime]
    
    created_at: datetime
