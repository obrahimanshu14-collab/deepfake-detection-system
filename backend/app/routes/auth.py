import os
import secrets

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.auth_utils import hash_password, create_access_token, verify_password
from app.database.connection import get_db
from app.database.models import User
from app.schemas import GoogleLoginRequest, Token, UserLogin, UserSignup

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
ADMIN_EMAILS = {
    item.strip().lower()
    for item in os.getenv("ADMIN_EMAILS", "").split(",")
    if item.strip()
}


def _token_for(user: User) -> str:
    return create_access_token({
        "user_id": user.id,
        "email": user.email,
        "is_admin": bool(user.is_admin),
    })


def _normalise_email(email: str) -> str:
    return email.strip().lower()


@router.post("/signup", response_model=Token)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    email = _normalise_email(str(user_data.email))
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = User(
        email=email,
        password_hash=hash_password(user_data.password),
        is_admin=email in ADMIN_EMAILS,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"access_token": _token_for(new_user)}


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    email = _normalise_email(str(user_data.email))
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return {"access_token": _token_for(user)}


@router.post("/google", response_model=Token)
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured on this server")

    try:
        idinfo = id_token.verify_oauth2_token(
            data.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    if not idinfo.get("email_verified"):
        raise HTTPException(status_code=400, detail="Google email is not verified")

    email = _normalise_email(idinfo["email"])
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(32)),
            is_admin=email in ADMIN_EMAILS,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"access_token": _token_for(user)}
