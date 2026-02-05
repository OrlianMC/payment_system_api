from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from sqlmodel import Session, select

from app.models import User
from app.services.user_service import UserService
from app.core.config import settings
from app.core.database import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return pwd_context.verify(password, hashed)

    @staticmethod
    def create_access_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        }
        return jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    def decode_access_token(token: str) -> int:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
                )
            return int(user_id)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
            )

    @staticmethod
    def get_current_user(
        token: str = Depends(lambda: None), session: Session = Depends(get_session)
    ) -> User:
        """
        Dependencia FastAPI para obtener el usuario actual desde JWT.
        """
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido"
            )
        user_id = AuthService.decode_access_token(token)
        user = UserService.get_by_id(session, user_id)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo"
            )
        return user

    @staticmethod
    def require_admin(current_user: User = Depends(get_current_user)):
        """
        Dependencia FastAPI para endpoints admin-only.
        """
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos"
            )
        return current_user

    @staticmethod
    def authenticate_user(
        session: Session, email: str, password: str
    ) -> Optional[User]:
        """
        Verifica credenciales de login.
        """
        user = UserService.get_by_email(session, email)
        if not user or not user.is_active:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
