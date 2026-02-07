from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.models import User
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.schemas import ProfileCreate, ProfileUpdate, ProfileRead
from app.core.database import get_session

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/", response_model=List[ProfileRead])
def list_profiles(
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.require_admin),
):
    return ProfileService.list_profiles(session, current_user)


@router.get("/me", response_model=ProfileRead)
def my_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return ProfileService.get_profile(session, current_user.id, current_user)


@router.get("/{user_id}", response_model=ProfileRead)
def get_profile(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return ProfileService.get_profile(session, user_id, current_user)


@router.post("/", response_model=ProfileRead)
def create_profile(
    profile_data: ProfileCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return ProfileService.create_profile(session, profile_data, current_user)


@router.put("/{user_id}", response_model=ProfileRead)
def update_profile(
    user_id: int,
    profile_data: ProfileUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return ProfileService.update_profile(session, user_id, profile_data, current_user)


@router.delete("/{user_id}", response_model=ProfileRead)
def delete_profile(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(AuthService.get_current_user),
):
    return ProfileService.delete_profile(session, user_id, current_user)
