from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.models.user_model import User
from .user_service import UserService
from app.core.config import settings
from app.core.database import get_session
from app.core.security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class AuthService:

    @staticmethod
    def create_access_token(user_id: int) -> str:

        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def create_service_token(service_name: str) -> str:

        payload = {
            "iss": "main-backend",
            "aud": "payment-service",
            "scope": "payments:write",
            "service": service_name,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(seconds=60),
        }

        return jwt.encode(
            payload,
            settings.INTERNAL_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @staticmethod
    def decode_access_token(token: str) -> int:

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )

            return int(user_id)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
    ) -> User:

        user_id = AuthService.decode_access_token(token)

        user = UserService.get_by_id(session, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive use",
            )

        return user

    @staticmethod
    def require_admin(
        current_user: User = Depends(get_current_user),
    ):

        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permissions",
            )

        return current_user

    @staticmethod
    def authenticate_user(
        session: Session,
        email: str,
        password: str,
    ) -> Optional[User]:

        user = UserService.get_by_email(session, email)

        if not user or not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user
