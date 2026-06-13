from fastapi import APIRouter

router = APIRouter()

@router.get("/test-user")
def test_user():
    return {"message": "User routes working"}