from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User
from app.schemas.clothing_schema import (
    ClothingCreate,
    ClothingUpdate
)
from app.services.auth_dependencies import get_current_user
from app.services.clothing_service import (
    create_clothing,
    get_user_clothing,
    update_clothing
)

router = APIRouter()


# -------------------------
# CREATE CLOTHING
# -------------------------
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
        "message": "Clothing added successfully!",
        "id": new_clothing.id,
        "name": new_clothing.name
    }


# -------------------------
# GET MY CLOTHES
# -------------------------
@router.get("/clothing")
def get_clothing(
    current_user: User = Depends(get_current_user)
):

    clothes = get_user_clothing(current_user.id)

    return clothes


# -------------------------
# UPDATE CLOTHING
# -------------------------
@router.put("/clothing/{clothing_id}")
def edit_clothing(
    clothing_id: int,
    clothing: ClothingUpdate,
    current_user: User = Depends(get_current_user)
):

    updated = update_clothing(
        clothing_id=clothing_id,
        user_id=current_user.id,
        name=clothing.name,
        category=clothing.category,
        color=clothing.color,
        season=clothing.season,
        style=clothing.style,
        brand=clothing.brand,
        image_url=clothing.image_url
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found."
        )

    return {
        "message": "Clothing updated successfully!",
        "clothing": updated
    }