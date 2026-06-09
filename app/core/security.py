import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def _create_token(sub: str, ttl: timedelta, token_type: Literal["access", "refresh"]) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": sub,
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(str(user_id), timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES), "access")


def create_refresh_token(user_id: int) -> str:
    return _create_token(str(user_id), timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS), "refresh")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(), algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
