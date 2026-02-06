import httpx
from fastapi import HTTPException, status
from typing import Dict
import logging
from app.services.auth_service import AuthService
from app.core.config import settings


class PaymentProcessorClient:

    def __init__(self, base_url: str = settings.PROCESSOR_URL):
        self.base_url = base_url.rstrip("/")

    async def process_payment(self, amount: float) -> Dict:

        payload = {"amount": amount}

        internal_token = AuthService.create_service_token(service_name="main-backend")
        logging.info(f"Generated internal token for payment processor: {internal_token}")
        logging.info("💛"*85)
        headers = {
            "Authorization": f"Bearer {internal_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/process-payment/",
                    json=payload,
                    headers=headers,
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
