from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from app.models import Card, User
from app.schemas import CardCreate, CardRead, CardUpdate


class CardService:

    @staticmethod
    def mask_card(number: str):
        last_four = number[-4:]
        masked = "**** **** **** " + last_four
        return last_four, masked

    @staticmethod
    def create_card(session: Session, data: CardCreate, current_user: User) -> CardRead:
        if current_user.role != "admin" and current_user.id != data.user_id:
            raise HTTPException(
                status_code=403, detail="You do not have permission to create this card"
            )

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
    def get_card(session: Session, card_id: int, current_user: User) -> CardRead:
        card = session.get(Card, card_id)
        if not card or card.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You do not have permission to view this card"
            )

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You do not have permission to update this card"
            )

        for k, v in data.items():
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You do not have permission to delete this card"
            )

        card.deleted_at = datetime.now(timezone.utc)
        session.add(card)
        session.commit()
        session.refresh(card)
        return CardRead.model_validate(card)
