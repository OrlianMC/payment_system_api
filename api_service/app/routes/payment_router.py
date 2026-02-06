from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.models import User
from app.services import AuthService, PaymentService
from app.schemas import PaymentCreate, PaymentRead
from app.core.database import get_session

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=List[PaymentRead])
def list_payments(
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    service = PaymentService(session)
    return service.list_payments(current_user)


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    service = PaymentService(session)
    return service.get_payment(payment_id, current_user)


@router.post("/", response_model=PaymentRead)
async def create_payment(
    payment_data: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    service = PaymentService(session)
    return await service.create_payment(current_user, payment_data)


@router.delete("/{payment_id}", response_model=PaymentRead)
def delete_payment(
    payment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    service = PaymentService(session)
    return service.delete_payment(payment_id, current_user)
