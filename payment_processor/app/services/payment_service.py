import random
import logging
from datetime import datetime, timezone
from decimal import Decimal

from app.schemas.payment_schemas import PaymentResponse

logger = logging.getLogger(__name__)


class PaymentProcessor:

    async def process_payment(self, amount: Decimal) -> PaymentResponse:

        processed_at = datetime.now(timezone.utc)

        if amount <= 0:
            logger.warning(
                "Payment rejected | reason=invalid_amount | amount=%s",
                amount,
            )

            return PaymentResponse(
                status="rejected",
                reference=None,
                reason="invalid_amount",
                processed_at=processed_at,
            )

        approved = random.random() < 0.8

        if approved:
            reference = f"REF-{int(processed_at.timestamp())}"

            logger.info(
                "Payment approved | reference=%s | amount=%s",
                reference,
                amount,
            )

            return PaymentResponse(
                status="approved",
                reference=reference,
                reason=None,
                processed_at=processed_at,
            )

        logger.warning(
            "Payment rejected | reason=insufficient_funds | amount=%s",
            amount,
        )

        return PaymentResponse(
            status="rejected",
            reference=None,
            reason="Insufficient Funds",
            processed_at=processed_at,
        )
