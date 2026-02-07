from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import List

from app.models import User
from app.schemas import UserCreate, UserRead, UserPasswordReset, UserUpdate
from app.core.security import hash_password, verify_password


class UserService:

    @staticmethod
    def get_by_email(session: Session, email: str) -> User:
        statement = select(User).where(User.email == email, User.deleted_at == None)
        return session.exec(statement).first()

    @staticmethod
    def get_by_id(session: Session, user_id: int) -> User:
        user = session.get(User, user_id)
        if not user or user.deleted_at:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    @staticmethod
    def list_users(session: Session, current_user: User) -> List[UserRead]:
        statement = select(User).where(User.deleted_at == None)

        if current_user.role != "admin":
            statement = statement.where(User.id == current_user.id)

        users = session.exec(statement).all()
        return [UserRead.model_validate(u) for u in users]

    @staticmethod
    def create_user(
        session: Session, user_data: UserCreate, current_user: User
    ) -> UserRead:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to create users",
            )

        if UserService.get_by_email(session, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return UserRead.model_validate(user)

    @staticmethod
    def update_user(
        session: Session, user_id: int, data: UserUpdate, current_user: User
    ) -> UserRead:
        user = UserService.get_by_id(session, user_id)

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this user",
            )
        if UserService.get_by_email(session, data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email already exists",
            )

        update_data = data.model_dump(exclude_unset=True)

        for k, v in update_data.items():
            setattr(user, k, v)
        user.updated_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
        session.refresh(user)
        return UserRead.model_validate(user)

    @staticmethod
    def delete_user(session: Session, user_id: int, current_user: User) -> UserRead:
        user = UserService.get_by_id(session, user_id)

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this user",
            )

        user.deleted_at = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
        session.refresh(user)
        return UserRead.model_validate(user)

    @staticmethod
    def change_password(
        session: Session, user_id: int, user_data: UserPasswordReset, current_user: User
    ) -> UserRead:
        user = UserService.get_by_id(session, user_id)

        if current_user.role != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to change this user's password",
            )

        if user_data.current_password and not verify_password(
            user_data.current_password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Incorrect current password",
            )

        user.hashed_password = hash_password(user_data.new_password)
        user.updated_at = datetime.now(timezone.utc)

        session.add(user)
        session.commit()
        session.refresh(user)

        return UserRead.model_validate(user)
