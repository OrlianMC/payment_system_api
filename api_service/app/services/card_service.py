from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List
import re

from app.models import Card, User, CardBrand
from app.schemas import CardCreate, CardRead, CardUpdate


class CardService:

    @staticmethod
    def validate_luhn(card_number: str) -> bool:
        digits = [int(d) for d in card_number]
        checksum = 0
        parity = len(digits) % 2

        for i, d in enumerate(digits):
            if i % 2 == parity:
                d *= 2
                if d > 9:
                    d -= 9
            checksum += d

        return checksum % 10 == 0

    @staticmethod
    def detect_brand(card_number: str) -> CardBrand:
        if card_number.startswith("4"):
            return CardBrand.visa
        if re.match(r"^5[1-5]", card_number):
            return CardBrand.mastercard
        if re.match(r"^3[47]", card_number):
            return CardBrand.amex
        raise HTTPException(
            status_code=400,
            detail="Unsupported card brand",
        )

    @staticmethod
    def mask_card(number: str):
        last_four = number[-4:]
        masked = "**** **** **** " + last_four
        return last_four, masked

    @staticmethod
    def validate_expiration(month: int, year: int):
        now = datetime.now(timezone.utc)
        if year < now.year or (year == now.year and month < now.month):
            raise HTTPException(
                status_code=400,
                detail="Card is expired",
            )

    @staticmethod
    def create_card(session: Session, data: CardCreate, current_user: User) -> CardRead:

        if current_user.role != "admin" and current_user.id != data.user_id:
            raise HTTPException(403, "Permission denied")

        card_number = data.card_number.replace(" ", "")

        if not re.fullmatch(r"\d{16}", card_number):
            raise HTTPException(400, "Card number must be 16 digits")

        if not CardService.validate_luhn(card_number):
            raise HTTPException(400, "Invalid card number")

        CardService.validate_expiration(
            data.expiration_month,
            data.expiration_year,
        )

        brand = CardService.detect_brand(card_number)

        last_four = card_number[-4:]
        existing = session.exec(
            select(Card).where(
                Card.user_id == data.user_id,
                Card.last_four == last_four,
                Card.deleted_at == None,
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Card already registered",
            )

        last_four, masked = CardService.mask_card(card_number)

        card = Card(
            user_id=data.user_id,
            card_holder_name=data.card_holder_name,
            brand=brand,
            last_four=last_four,
            masked_number=masked,
            expiration_month=data.expiration_month,
            expiration_year=data.expiration_year,
        )

        session.add(card)
        session.commit()
        session.refresh(card)

        return CardRead.model_validate(card)

    @staticmethod
    def get_card(session: Session, card_id: int, current_user: User) -> CardRead:
        card = session.get(Card, card_id)

        if not card or card.deleted_at:
            raise HTTPException(404, "Card not found")

        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(403, "Permission denied")

        return CardRead.model_validate(card)

    @staticmethod
    def list_cards(session: Session, current_user: User) -> List[CardRead]:

        statement = select(Card).where(Card.deleted_at == None)

        if current_user.role != "admin":
            statement = statement.where(Card.user_id == current_user.id)

        cards = session.exec(statement).all()

        return [CardRead.model_validate(c) for c in cards]

    @staticmethod
    def update_card(
        session: Session, card_id: int, data: CardUpdate, current_user: User
    ) -> CardRead:

        card = session.get(Card, card_id)

        if not card or card.deleted_at:
            raise HTTPException(404, "Card not found")

        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(403, "Permission denied")

        update_data = data.model_dump(exclude_unset=True)

        forbidden = {"last_four", "masked_number"}
        if any(f in update_data for f in forbidden):
            raise HTTPException(
                status_code=400,
                detail="Sensitive fields cannot be modified",
            )

        if "expiration_month" in update_data or "expiration_year" in update_data:
            month = update_data.get("expiration_month", card.expiration_month)
            year = update_data.get("expiration_year", card.expiration_year)
            CardService.validate_expiration(month, year)

        for k, v in update_data.items():
            setattr(card, k, v)

        card.updated_at = datetime.now(timezone.utc)

        session.add(card)
        session.commit()
        session.refresh(card)

        return CardRead.model_validate(card)

    @staticmethod
    def delete_card(session: Session, card_id: int, current_user: User) -> CardRead:

        card = session.get(Card, card_id)

        if not card or card.deleted_at:
            raise HTTPException(404, "Card not found")

        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(403, "Permission denied")

        card.deleted_at = datetime.now(timezone.utc)

        session.add(card)
        session.commit()
        session.refresh(card)

        return CardRead.model_validate(card)
