from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.services.auth_service import AuthService, UserService
from app.schemas import UserCreate, UserRead, UserPasswordReset
from app.core.database import get_session

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    return UserService.create_user(session, user_data)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):

    user = AuthService.authenticate_user(
        session,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not valid credentials"
        )

    token = AuthService.create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/change-password", response_model=UserRead)
def change_password(
    user_data: UserPasswordReset,
    current_user=Depends(AuthService.get_current_user),
    session: Session = Depends(get_session),
):
    return UserService.change_password(session, current_user.id, user_data)
