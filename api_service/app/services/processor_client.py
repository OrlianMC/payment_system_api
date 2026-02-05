import httpx
from fastapi import HTTPException, status
from typing import Dict
from app.core.config import settings


class PaymentProcessorClient:
    """
    Cliente para comunicarse con el microservicio externo de procesamiento de pagos.
    """

    def __init__(self, base_url: str = settings.PROCESSOR_URL):
        self.base_url = base_url.rstrip("/")

    async def process_payment(self, amount: float) -> Dict:
        """
        Envía la solicitud de pago al microservicio externo.
        Devuelve un dict con:
            {
                "status": "approved" | "rejected",
                "reference": "xxxx"  # opcional
            }
        """

        payload = {"amount": amount}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/process-payment", json=payload
                )
                response.raise_for_status()
                data = response.json()

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payment processor unreachable: {e}",
            )

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment processor error: {e.response.text}",
            )

        if "status" not in data:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from payment processor",
            )

        return data
