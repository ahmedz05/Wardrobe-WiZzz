from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.user_service import create_user, verify_password
from app.services.auth_service import create_access_token

from app.services.auth_dependencies import get_current_user
from fastapi import Depends

router = APIRouter()


# -----------------------
# REGISTER
# -----------------------
@router.post("/register")
def register(user: UserCreate):

    new_user = create_user(
        username=user.username,
        email=user.email,
        password=user.password
    )

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }


# -----------------------
# LOGIN
# -----------------------
@router.post("/login")
def login(user: UserLogin):

    db: Session = SessionLocal()

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -----------------------
# ME (TEST AUTH)
# -----------------------
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }