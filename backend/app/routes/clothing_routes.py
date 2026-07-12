from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.clothing_schema import ClothingCreate
from app.services.auth_dependencies import get_current_user
from app.services.clothing_service import (
    create_clothing,
    get_user_clothing
)

router = APIRouter()


@router.post("/clothing")
def add_clothing(
    clothing: ClothingCreate,
    current_user: User = Depends(get_current_user)
):

    new_clothing = create_clothing(
        user_id=current_user.id,
        name=clothing.name,
        category=clothing.category,
        color=clothing.color,
        season=clothing.season,
        style=clothing.style,
        brand=clothing.brand,
        image_url=clothing.image_url
    )

    return {
        "message": "Clothing added successfully",
        "id": new_clothing.id,
        "name": new_clothing.name
    }


@router.get("/clothing")
def get_clothing(
    current_user: User = Depends(get_current_user)
):

    clothes = get_user_clothing(current_user.id)

    return clothes