from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from app.models import Profile, User
from app.schemas import ProfileCreate, ProfileUpdate, ProfileRead


class ProfileService:

    @staticmethod
    def _get_active_profile(session: Session, user_id: int) -> Profile | None:
        return session.exec(
            select(Profile).where(
                Profile.user_id == user_id,
                Profile.deleted_at == None,
            )
        ).first()

    @staticmethod
    def get_profile(session: Session, user_id: int, current_user: User) -> ProfileRead:

        profile = ProfileService._get_active_profile(session, user_id)

        if not profile:
            raise HTTPException(404, "Profile not found")

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(403, "Forbidden")

        return ProfileRead.model_validate(profile)

    @staticmethod
    def list_profiles(session: Session, current_user: User) -> List[ProfileRead]:

        statement = select(Profile).where(Profile.deleted_at == None)

        if current_user.role != "admin":
            statement = statement.where(Profile.user_id == current_user.id)

        profiles = session.exec(statement).all()

        return [ProfileRead.model_validate(p) for p in profiles]

    @staticmethod
    def create_profile(
        session: Session, profile_data: ProfileCreate, current_user: User
    ) -> ProfileRead:

        existing_profile = ProfileService._get_active_profile(session, current_user.id)

        if existing_profile:
            raise HTTPException(400, "Profile already exists")

        profile = Profile(
            user_id=current_user.id,
            **profile_data.model_dump(exclude_unset=True),
        )

        session.add(profile)
        session.commit()
        session.refresh(profile)

        return ProfileRead.model_validate(profile)

    @staticmethod
    def update_profile(
        session: Session,
        user_id: int,
        profile_data: ProfileUpdate,
        current_user: User,
    ) -> ProfileRead:

        profile = ProfileService._get_active_profile(session, user_id)

        if not profile:
            raise HTTPException(404, "Profile not found")

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(403, "Forbidden")

        update_data = profile_data.model_dump(exclude_unset=True)

        for k, v in update_data.items():
            setattr(profile, k, v)

        profile.updated_at = datetime.now(timezone.utc)

        session.add(profile)
        session.commit()
        session.refresh(profile)

        return ProfileRead.model_validate(profile)

    @staticmethod
    def delete_profile(
        session: Session,
        user_id: int,
        current_user: User,
    ) -> ProfileRead:

        profile = ProfileService._get_active_profile(session, user_id)

        if not profile:
            raise HTTPException(404, "Profile not found")

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(403, "Forbidden")

        profile.deleted_at = datetime.now(timezone.utc)

        session.add(profile)
        session.commit()
        session.refresh(profile)

        return ProfileRead.model_validate(profile)
