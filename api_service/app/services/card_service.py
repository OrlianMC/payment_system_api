from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from app.models import Card
from app.schemas import CardCreate, CardRead


class CardService:

    @staticmethod
    def mask_card(number: str):
        """Genera last_four y masked_number de la tarjeta"""
        last_four = number[-4:]
        masked = "**** **** **** " + last_four
        return last_four, masked

    @staticmethod
    def create_card(session: Session, data: CardCreate) -> CardRead:
        last_four, masked = CardService.mask_card(data.card_number)
        card = Card(
            user_id=data.user_id,
            card_holder_name=data.card_holder_name,
            brand=data.brand,
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
    def get_card(session: Session, card_id: int) -> CardRead:
        card = session.get(Card, card_id)
        if not card or card.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )
        return CardRead.model_validate(card)

    @staticmethod
    def list_cards(session: Session, user_id: int = None) -> List[CardRead]:
        statement = select(Card).where(Card.deleted_at == None)
        if user_id:
            statement = statement.where(Card.user_id == user_id)
        cards = session.exec(statement).all()
        return [CardRead.model_validate(c) for c in cards]

    @staticmethod
    def update_card(session: Session, card_id: int, data: dict) -> CardRead:
        card = session.get(Card, card_id)
        if not card or card.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        for k, v in data.items():
            setattr(card, k, v)
        card.updated_at = datetime.now(timezone.utc)
        session.add(card)
        session.commit()
        session.refresh(card)
        return CardRead.model_validate(card)

    @staticmethod
    def delete_card(session: Session, card_id: int) -> CardRead:
        card = session.get(Card, card_id)
        if not card or card.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )
        card.deleted_at = datetime.now(timezone.utc)
        session.add(card)
        session.commit()
        session.refresh(card)
        return CardRead.model_validate(card)
