from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from app.models import Profile
from app.schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileRead,
)
from app.services import AuthService, UserService


class ProfileService:

    @staticmethod
    def get_profile(session: Session, user_id: int) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if not user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )
        return ProfileRead.model_validate(user.profile)

    @staticmethod
    def list_profiles(session: Session) -> List[ProfileRead]:
        statement = select(Profile).where(Profile.deleted_at == None)
        profiles = session.exec(statement).all()
        return [ProfileRead.model_validate(p) for p in profiles]

    @staticmethod
    def create_profile(
        session: Session, user_id: int, profile_data: ProfileCreate
    ) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if user.profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists"
            )

        profile = Profile(
            user_id=user.id, **profile_data.model_dump(exclude_unset=True)
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return ProfileRead.model_validate(profile)

    @staticmethod
    def update_profile(
        session: Session, user_id: int, profile_data: ProfileUpdate
    ) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if not user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        profile_data_dict = profile_data.model_dump(exclude_unset=True)
        for k, v in profile_data_dict.items():
            setattr(user.profile, k, v)

        user.profile.updated_at = datetime.now(timezone.utc)
        session.add(user.profile)
        session.commit()
        session.refresh(user.profile)
        return ProfileRead.model_validate(user.profile)

    @staticmethod
    def delete_profile(session: Session, user_id: int) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if not user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        user.profile.deleted_at = datetime.now(timezone.utc)
        session.add(user.profile)
        session.commit()
        session.refresh(user.profile)
        return ProfileRead.model_validate(user.profile)
