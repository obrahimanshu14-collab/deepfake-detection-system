from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY in {"change-me", "any-random-string-here"}:
    raise RuntimeError("SECRET_KEY is not configured. Set a strong random value in the environment.")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
FREE_TRIAL_LIMIT = int(os.getenv("FREE_TRIAL_LIMIT", "5"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=True)


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = utc_now_naive() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("missing user_id")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def check_and_consume_trial(current_user: User, db: Session) -> None:
    if current_user.has_premium:
        if current_user.premium_expires_at and current_user.premium_expires_at < utc_now_naive():
            current_user.has_premium = False
            current_user.premium_expires_at = None
            db.commit()
        else:
            return

    if current_user.free_trials_used >= FREE_TRIAL_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Free trial limit reached. Please upgrade to continue.",
        )

    current_user.free_trials_used += 1
    db.add(current_user)
    db.commit()
