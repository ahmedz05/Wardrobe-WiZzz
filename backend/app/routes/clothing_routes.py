from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from app.schemas.clothing_schema import (
    ClothingCreate,
    ClothingUpdate,
    ClothingResponse,
)

from app.services.auth_dependencies import get_current_user

from app.services.clothing_service import (
    create_clothing,
    get_user_clothing,
    update_clothing,
    delete_clothing,
)

from app.services.wardrobe_matching_service import (
    rank_wardrobe_color_matches,
)


router = APIRouter()


# -------------------------
# CREATE CLOTHING
# -------------------------

@router.post(
    "/clothing",
    response_model=ClothingResponse,
)
def add_clothing(
    clothing: ClothingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_clothing = create_clothing(
            db=db,
            user_id=current_user.id,
            clothing=clothing,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return new_clothing


# -------------------------
# GET MY CLOTHES
# -------------------------

@router.get(
    "/clothing",
    response_model=list[ClothingResponse],
)
def get_clothing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_clothing(
        db=db,
        user_id=current_user.id,
    )


# -------------------------
# GET CLOTHING MATCHES
# -------------------------

@router.get(
    "/clothing/{clothing_id}/matches"
)
def get_clothing_matches(
    clothing_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return rank_wardrobe_color_matches(
            db=db,
            user_id=current_user.id,
            clothing_id=clothing_id,
            limit=limit,
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Clothing item not found.":
            raise HTTPException(
                status_code=404,
                detail=message,
            )

        raise HTTPException(
            status_code=400,
            detail=message,
        )


# -------------------------
# UPDATE CLOTHING
# -------------------------

@router.put(
    "/clothing/{clothing_id}",
    response_model=ClothingResponse,
)
def edit_clothing(
    clothing_id: int,
    clothing: ClothingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        updated = update_clothing(
            db=db,
            clothing_id=clothing_id,
            user_id=current_user.id,
            clothing_data=clothing,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found.",
        )

    return updated


# -------------------------
# DELETE CLOTHING
# -------------------------

@router.delete(
    "/clothing/{clothing_id}"
)
def remove_clothing(
    clothing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_clothing(
        db=db,
        clothing_id=clothing_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found.",
        )

    return {
        "message": "Clothing deleted successfully!",
    }