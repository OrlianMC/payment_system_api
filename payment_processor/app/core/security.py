from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

security = HTTPBearer()

def verify_internal_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization token",
        )

    token = credentials.credentials.strip()

    try:
        payload = jwt.decode(
            token,
            settings.INTERNAL_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.EXPECTED_AUDIENCE,
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )

    if payload.get("iss") != settings.EXPECTED_ISSUER:
        raise HTTPException(status_code=401, detail="Invalid issuer")

    if payload.get("aud") != settings.EXPECTED_AUDIENCE:
        raise HTTPException(status_code=401, detail="Invalid audience")

    if payload.get("scope") != settings.EXPECTED_SCOPE:
        raise HTTPException(status_code=403, detail="Invalid scope")

    return payload
