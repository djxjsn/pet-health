from typing import Optional
from sqlalchemy.orm import Session
from src.models.user import User
from src.models.user_profile import UserProfile
from src.schemas.user import UserCreate, UserProfileCreate
from src.core.security import hash_password


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    return db.query(User).filter(User.phone == phone).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        phone=user_data.phone,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_profile(db: Session, user_id: str, profile_data: UserProfileCreate) -> UserProfile:
    profile = UserProfile(
        user_id=user_id,
        full_name=profile_data.full_name,
        gender=profile_data.gender,
        date_of_birth=profile_data.date_of_birth,
        avatar_url=profile_data.avatar_url,
        address=profile_data.address,
        bio=profile_data.bio,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_user_login_time(db: Session, user_id: str) -> None:
    from datetime import datetime
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login_at = datetime.utcnow()
        db.commit()
