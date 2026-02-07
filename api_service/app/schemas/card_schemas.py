from datetime import datetime, date
from typing import Optional, Annotated

from sqlmodel import SQLModel
from pydantic import field_validator, StringConstraints, Field

from app.models import CardBrand

CardNumber = Annotated[
    str,
    StringConstraints(pattern=r"^\d{16}$", strip_whitespace=True),
]

ExpirationMonth = Annotated[
    int,
    Field(ge=1, le=12),
]


class CardCreate(SQLModel):
    user_id: int
    card_holder_name: str
    # brand: CardBrand

    card_number: CardNumber
    expiration_month: ExpirationMonth
    expiration_year: int

    @field_validator("expiration_year")
    @classmethod
    def validate_future_date(cls, year, info):
        month = info.data.get("expiration_month")
        if month:
            today = date.today()
            exp_date = date(year, month, 1)
            if exp_date < date(today.year, today.month, 1):
                raise ValueError("Card is expired")
        return year


class CardUpdate(SQLModel):
    card_holder_name: Optional[str] = None
    brand: Optional[CardBrand] = None

    expiration_month: Optional[ExpirationMonth] = None
    expiration_year: Optional[int] = None

    is_active: Optional[bool] = None

    @field_validator("expiration_year")
    @classmethod
    def validate_future_date(cls, year, info):
        month = info.data.get("expiration_month")
        if month and year:
            today = date.today()
            exp_date = date(year, month, 1)
            if exp_date < date(today.year, today.month, 1):
                raise ValueError("Card is expired")
        return year


class CardRead(SQLModel):
    id: int
    user_id: int

    card_holder_name: str
    brand: CardBrand

    last_four: str
    masked_number: str

    expiration_month: int
    expiration_year: int

    is_active: bool
    created_at: datetime
