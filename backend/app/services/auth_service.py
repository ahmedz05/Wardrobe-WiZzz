import os
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError


# =========================
# JWT CONFIGURATION
# =========================

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# CREATE ACCESS TOKEN
# =========================

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================
# VERIFY ACCESS TOKEN
# =========================

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require_exp": True
            }
        )

        return payload

    except (JWTError, TypeError, ValueError, OverflowError):
        return None