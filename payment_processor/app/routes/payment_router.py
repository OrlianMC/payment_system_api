from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.payment_schemas import PaymentRequest, PaymentResponse
from app.services.payment_service import PaymentProcessor
from app.core.security import verify_internal_token

router = APIRouter(prefix="/process-payment", tags=["Payments"])
processor = PaymentProcessor()


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def process_payment(
    req: PaymentRequest,
    token_data=Depends(verify_internal_token),
):
    try:
        result = await processor.process_payment(req.amount)
        return result

    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
