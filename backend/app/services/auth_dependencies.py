from typing import NoReturn

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import verify_token

# This replaces OAuth2PasswordBearer (fixes Swagger confusion)
oauth2_scheme = HTTPBearer()


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Extract raw token string
    jwt_token = token.credentials

    # Decode JWT
    payload = verify_token(jwt_token)

    user_id = payload.get("user_id") if payload else None
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Find user from token payload
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def require_catalog_write_access(
    current_user: User = Depends(get_current_user),
) -> NoReturn:
    """Authenticate first, then deny writes until catalog privileges are defined.

    No account or token claim can bypass this temporary policy. Keep this
    dependency on mutation operations only so public catalog reads stay public.
    """
    raise HTTPException(status_code=403, detail="Shared catalog mutations are disabled.")
