# app/routers/card_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.models import User
from app.services import AuthService, CardService
from app.schemas import CardCreate, CardRead, CardUpdate
from app.core.database import get_session

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get("/", response_model=List[CardRead])
def list_cards(
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return CardService.list_cards(session, current_user)


@router.get("/{card_id}", response_model=CardRead)
def get_card(
    card_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return CardService.get_card(session, card_id, current_user)


@router.post("/", response_model=CardRead)
def create_card(
    card_data: CardCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.require_admin),
):
    if card_data.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="You cannot create cards for another user"
        )
    return CardService.create_card(session, card_data, current_user)


@router.put("/{card_id}", response_model=CardRead)
def update_card(
    card_id: int,
    data: CardUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.require_admin),
):
    return CardService.update_card(session, card_id, data, current_user)


@router.delete("/{card_id}", response_model=CardRead)
def delete_card(
    card_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.require_admin),
):
    return CardService.delete_card(session, card_id, current_user)
