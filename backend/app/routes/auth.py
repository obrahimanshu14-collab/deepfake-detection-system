import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.database.connection import get_db
from app.database.models import User
from app.schemas import UserSignup, UserLogin, Token, GoogleLoginRequest
from app.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/signup", response_model=Token)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({
        "user_id": new_user.id, "email": new_user.email, "is_admin": new_user.is_admin,
    })
    return {"access_token": token}


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id, "email": user.email, "is_admin": user.is_admin,
    })
    return {"access_token": token}


@router.post("/google", response_model=Token)
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(
            data.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = idinfo["email"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, password_hash=hash_password(os.urandom(16).hex()))
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({
        "user_id": user.id, "email": user.email, "is_admin": user.is_admin,
    })
    return {"access_token": token}