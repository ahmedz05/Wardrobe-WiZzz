from fastapi import APIRouter
from app.schemas.user_schema import UserCreate
from app.services.user_service import create_user

router = APIRouter()

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