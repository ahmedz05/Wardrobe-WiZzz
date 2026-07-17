from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.models.user import User

from app.schemas.clothing_schema import (
    ClothingCreate,
    ClothingUpdate
)

from app.services.auth_dependencies import get_current_user

from app.services.clothing_service import (
    create_clothing,
    get_user_clothing,
    update_clothing,
    delete_clothing,
    upload_clothing_image
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

        subcategory_id=clothing.subcategory_id,

        color=clothing.color,

        fit=clothing.fit,

        material=clothing.material,

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

    clothes = get_user_clothing(
        current_user.id
    )

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

        subcategory_id=clothing.subcategory_id,

        color=clothing.color,

        fit=clothing.fit,

        material=clothing.material,

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


# -------------------------
# DELETE CLOTHING
# -------------------------

@router.delete("/clothing/{clothing_id}")
def remove_clothing(
    clothing_id: int,
    current_user: User = Depends(get_current_user)
):

    deleted = delete_clothing(
        clothing_id=clothing_id,

        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found."
        )

    return {
        "message": "Clothing deleted successfully!"
    }


# -------------------------
# UPLOAD CLOTHING IMAGE
# -------------------------

@router.post("/clothing/{clothing_id}/image")
def upload_image(
    clothing_id: int,

    file: UploadFile = File(...),

    current_user: User = Depends(get_current_user)
):

    clothing = upload_clothing_image(
        clothing_id=clothing_id,

        user_id=current_user.id,

        file=file
    )

    if not clothing:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found or invalid image."
        )

    return {
        "message": "Image uploaded successfully!",

        "image_url": clothing.image_url,

        "clothing": clothing
    }