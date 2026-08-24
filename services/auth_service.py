"""Authentication service: user CRUD and authentication helpers."""
from typing import Optional
from sqlalchemy.orm import Session

from db.models import User
from core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None, role: Optional[str] = None) -> User:
    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("User with this email already exists")
    hashed = get_password_hash(password)
    user = User(email=email, hashed_password=hashed, full_name=full_name, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user