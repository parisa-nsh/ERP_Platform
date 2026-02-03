"""JWT and password hashing."""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.models.user import Role

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    email: str,
    role: Role,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, int]:
    """Return (token, expires_in_seconds)."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "role": role.value,
        "exp": expire,
        "type": "access",
    }
    encoded = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    return encoded, expires_in


def decode_token(token: str) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
