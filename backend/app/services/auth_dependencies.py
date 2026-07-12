from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import verify_token

# This replaces OAuth2PasswordBearer (fixes Swagger confusion)
oauth2_scheme = HTTPBearer()


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    # Extract raw token string
    jwt_token = token.credentials

    # Decode JWT
    payload = verify_token(jwt_token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Connect to DB
    db: Session = SessionLocal()

    # Find user from token payload
    user = db.query(User).filter(User.id == payload["user_id"]).first()

    db.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user