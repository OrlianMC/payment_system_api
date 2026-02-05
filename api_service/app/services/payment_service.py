from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional, List

from app.models import Payment, PaymentStatus
from app.schemas import PaymentCreate, PaymentRead
from app.services import CardService, PaymentProcessorClient


class PaymentService:
    """
    Service de pagos que se comunica con un PaymentProcessor externo.
    """

    def __init__(self, session: Session):
        self.session = session
        self.processor_client = PaymentProcessorClient()
        self.card_service = CardService()

    async def create_payment(
        self,
        current_user,
        payment_data: PaymentCreate
    ) -> PaymentRead:
        """Crear un pago y procesarlo vía microservicio"""

        # Validaciones básicas
        if payment_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El monto del pago debe ser mayor a 0"
            )

        card = self.card_service.get_card(self.session, payment_data.card_id)
        if card.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La tarjeta no pertenece al usuario"
            )

        if payment_data.model_dump().get("idempotency_key"):
            existing = self.session.exec(
                select(Payment).where(Payment.idempotency_key == payment_data.idempotency_key)
            ).first()
            if existing:
                return PaymentRead.model_validate(existing)

        payment = Payment(
            user_id=current_user.id,
            card_id=payment_data.card_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status=PaymentStatus.pending,
            idempotency_key=getattr(payment_data, "idempotency_key", None)
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

    def get_payment(self, payment_id: int, current_user) -> PaymentRead:
        payment = self.session.get(Payment, payment_id)
        if not payment or payment.deleted_at:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")

        if current_user.role != "admin" and payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

        return PaymentRead.model_validate(payment)

    def list_payments(self, current_user, user_id: Optional[int] = None) -> List[PaymentRead]:
        statement = select(Payment).where(Payment.deleted_at == None)

        if user_id:
            if current_user.role != "admin" and user_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
            statement = statement.where(Payment.user_id == user_id)
        elif current_user.role != "admin":
            statement = statement.where(Payment.user_id == current_user.id)

        payments = self.session.exec(statement).all()
        return [PaymentRead.model_validate(p) for p in payments]

    def delete_payment(self, payment_id: int, current_user) -> PaymentRead:
        payment = self.session.get(Payment, payment_id)
        if not payment or payment.deleted_at:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")

        if current_user.role != "admin" and payment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

        payment.deleted_at = datetime.now(timezone.utc)
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)

        return PaymentRead.model_validate(payment)
