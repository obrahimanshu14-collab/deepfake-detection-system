import hashlib
import os
import secrets
from datetime import timedelta

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth_utils import utc_now_naive
from app.database.connection import get_db
from app.database.models import ApiKey, UsageLog

API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
API_DAILY_LIMIT = int(os.getenv("API_DAILY_LIMIT", "100"))
api_key_scheme = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key() -> tuple[str, str]:
    raw_key = f"vrs_live_{secrets.token_urlsafe(32)}"
    return raw_key, hash_api_key(raw_key)


def get_api_key_record(
    raw_key: str | None = Security(api_key_scheme),
    db: Session = Depends(get_db),
) -> ApiKey:
    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing {API_KEY_HEADER} header",
        )

    record = db.query(ApiKey).filter(
        ApiKey.key_hash == hash_api_key(raw_key),
        ApiKey.is_active.is_(True),
    ).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    since = utc_now_naive() - timedelta(days=1)
    calls = (
        db.query(func.count(UsageLog.id))
        .filter(UsageLog.api_key_id == record.id, UsageLog.called_at >= since)
        .scalar()
        or 0
    )
    if calls >= API_DAILY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="API daily request limit reached",
            headers={"Retry-After": "86400"},
        )

    return record
