import os
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth_utils import create_access_token, hash_password, verify_password
from app.database.connection import get_db
from app.database.models import User
from app.schemas import GoogleCredential, Token, UserLogin, UserSignup

router = APIRouter(prefix="/auth", tags=["Authentication"])
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def _issue_token(user: User) -> dict:
    return {
        "access_token": create_access_token(
            {"user_id": user.id, "email": user.email, "is_admin": user.is_admin}
        )
    }


@router.post("/signup", response_model=Token)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    email = user_data.email.strip().lower()
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in instead.",
        )

    new_user = User(email=email, password_hash=hash_password(user_data.password))
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in instead.",
        )
    db.refresh(new_user)

    return _issue_token(new_user)


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    email = user_data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return _issue_token(user)


@router.post("/google", response_model=Token)
def google_login(payload: GoogleCredential, db: Session = Depends(get_db)):
    """Verify a Google Identity Services ID token server-side and issue our own JWT."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server yet.",
        )

    try:
        google_user = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google sign-in could not be verified. Please try again.",
        ) from exc

    email = (google_user.get("email") or "").strip().lower()
    if not email or not google_user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google did not provide a verified email address.",
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        # Google-authenticated accounts do not use password login. A random
        # hash keeps the existing schema compatible without storing a
        # plaintext password or adding a migration just for the MVP flow.
        user = User(email=email, password_hash=hash_password(secrets.token_urlsafe(32)))
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not create the Google account. Please try again.",
                )
        else:
            db.refresh(user)

    return _issue_token(user)
