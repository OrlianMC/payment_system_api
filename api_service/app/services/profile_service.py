from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from app.models import Profile, User
from app.schemas import ProfileCreate, ProfileUpdate, ProfileRead
from .user_service import UserService


class ProfileService:

    @staticmethod
    def get_profile(session: Session, user_id: str, current_user: User) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if not user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this profile",
            )

        return ProfileRead.model_validate(user.profile)

    @staticmethod
    def list_profiles(session: Session, current_user: User) -> List[ProfileRead]:
        statement = select(Profile).where(Profile.deleted_at == None)

        if current_user.role != "admin":
            statement = statement.where(Profile.user_id == current_user.id)

        profiles = session.exec(statement).all()
        return [ProfileRead.model_validate(p) for p in profiles]

    @staticmethod
    def create_profile(
        session: Session, user_id: int, profile_data: ProfileCreate, current_user: User
    ) -> ProfileRead:
        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to create this profile",
            )

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
        session: Session, user_id: int, profile_data: ProfileUpdate, current_user: User
    ) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if not user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this profile",
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
    def delete_profile(
        session: Session, user_id: int, current_user: User
    ) -> ProfileRead:
        user = UserService.get_by_id(session, user_id)
        if not user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this profile",
            )

        user.profile.deleted_at = datetime.now(timezone.utc)
        session.add(user.profile)
        session.commit()
        session.refresh(user.profile)
        return ProfileRead.model_validate(user.profile)
