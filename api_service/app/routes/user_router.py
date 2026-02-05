from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
from app.services import AuthService, UserService
from app.schemas import UserRead, UserUpdate
from app.core.database import get_session

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserRead])
def list_users(
    session: Session = Depends(get_session),
    current_user=Depends(AuthService.require_admin),
):
    return UserService.list_users(session)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(AuthService.require_admin),
):
    return UserService.get_by_id(session, user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(AuthService.require_admin),
):
    return UserService.update_user(session, user_id, data)


@router.delete("/{user_id}", response_model=UserRead)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(AuthService.require_admin),
):
    return UserService.delete_user(session, user_id)
