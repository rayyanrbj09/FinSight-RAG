from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from core.security import create_access_token, create_refresh_token, get_current_user
from db.crud import authenticate_user, create_user, get_user_by_email, get_user_by_username
from db.database import get_db
from db.models import User

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new user and return JWT tokens."""
    email = payload.email.lower().strip()
    username = payload.username.strip()

    if get_user_by_email(db, email) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if get_user_by_username(db, username) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    user = create_user(
        db=db,
        email=email,
        username=username,
        password=payload.password,
        full_name=payload.full_name,
    )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate a user and return JWT tokens."""
    identifier = payload.email.lower().strip() if payload.email else payload.username.strip() if payload.username else ""
    user = authenticate_user(db, identifier, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's profile."""
    return current_user
