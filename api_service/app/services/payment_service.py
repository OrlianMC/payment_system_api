from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional, List
import logging

from app.models import Payment, PaymentStatus, User
from app.schemas import PaymentCreate, PaymentRead
from .card_service import CardService
from .processor_client import PaymentProcessorClient


class PaymentService:

    def __init__(self, session: Session):
        self.session = session
        self.processor_client = PaymentProcessorClient()
        self.card_service = CardService()

    async def create_payment(
        self, current_user: User, payment_data: PaymentCreate
    ) -> PaymentRead:

        if payment_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The payment amount must be greater than 0",
            )

        card = self.card_service.get_card(
            self.session, payment_data.card_id, current_user
        )
        if current_user.role != "admin" and card.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The card does not belong to the user",
            )

        if payment_data.idempotency_key:
            existing = self.session.exec(
                select(Payment).where(
                    Payment.idempotency_key == payment_data.idempotency_key,
                    Payment.deleted_at == None,
                )
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Payment with this idempotency key already exists",
                        "payment_id": existing.id,
                        "status": existing.status,
                    },
                )

        payment = Payment(
            user_id=current_user.id,
            card_id=payment_data.card_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status=PaymentStatus.pending,
            idempotency_key=getattr(payment_data, "idempotency_key", None),
        )

        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        result = await self.processor_client.process_payment(payment.amount)

        if result["status"] == "approved":
            payment.status = PaymentStatus.approved
            payment.processor_reference = result.get("reference")
            payment.processed_at = datetime.now(timezone.utc)
        else:
            payment.status = PaymentStatus.rejected
            payment.status_reason = result.get("reason", "Rejected by processor")

        payment.updated_at = datetime.now(timezone.utc)
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return PaymentRead.model_validate(payment)

    def get_payment(self, payment_id: int, current_user: User) -> PaymentRead:
        payment = self.session.get(Payment, payment_id)
        if not payment or payment.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )

        if current_user.role != "admin" and payment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this payment",
            )

        return PaymentRead.model_validate(payment)

    def list_payments(self, current_user: User) -> List[PaymentRead]:
        statement = select(Payment).where(Payment.deleted_at == None)

        if current_user.role != "admin":
            statement = statement.where(Payment.user_id == current_user.id)

        payments = self.session.exec(statement).all()
        return [PaymentRead.model_validate(p) for p in payments]

    def delete_payment(self, payment_id: int, current_user: User) -> PaymentRead:
        payment = self.session.get(Payment, payment_id)
        if not payment or payment.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
            )

        if current_user.role != "admin" and payment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this payment",
            )

        payment.deleted_at = datetime.now(timezone.utc)
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return PaymentRead.model_validate(payment)
