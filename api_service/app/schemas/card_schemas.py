from datetime import datetime
from sqlmodel import SQLModel
from app.models import CardBrand


class CardCreate(SQLModel):
    user_id: int
    card_holder_name: str
    brand: CardBrand

    card_number: str
    expiration_month: int
    expiration_year: int


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
