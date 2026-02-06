from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Literal


class PaymentRequest(BaseModel):
    amount: Decimal = Field(
        gt=0, description="Payment amount. Must be greater than zero."
    )


class PaymentResponse(BaseModel):
    status: Literal["approved", "rejected"]
    reference: str | None = None
    reason: str | None = None
    processed_at: datetime
