
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
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


# =====================================
# DATABASE CONSTRAINT ERROR MESSAGE
# =====================================

CONSTRAINT_ERROR_MESSAGE = (
    "Clothing data violates database constraints."
)


# =====================================
# CREATE CLOTHING
# =====================================

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

    except ValueError as exc:
        # Business validation error.
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        # Database constraint violation.
        # Do not expose SQL statements or database details.
        raise HTTPException(
            status_code=409,
            detail=CONSTRAINT_ERROR_MESSAGE,
        ) from exc

    return new_clothing


# =====================================
# GET MY CLOTHING
# =====================================

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


# =====================================
# GET CLOTHING MATCHES
# =====================================

@router.get(
    "/clothing/{clothing_id}/matches",
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
            ) from exc

        raise HTTPException(
            status_code=400,
            detail=message,
        ) from exc


# =====================================
# UPDATE CLOTHING
# =====================================

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

    except ValueError as exc:
        # Invalid clothing data or catalog selection.
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        # Constraint violation during update.
        # Never return raw database error messages.
        raise HTTPException(
            status_code=409,
            detail=CONSTRAINT_ERROR_MESSAGE,
        ) from exc

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found.",
        )

    return updated


# =====================================
# DELETE CLOTHING
# =====================================

@router.delete(
    "/clothing/{clothing_id}",
)
def remove_clothing(
    clothing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        deleted = delete_clothing(
            db=db,
            clothing_id=clothing_id,
            user_id=current_user.id,
        )

    except IntegrityError as exc:
        # A database constraint prevented deletion.
        raise HTTPException(
            status_code=409,
            detail=CONSTRAINT_ERROR_MESSAGE,
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Clothing item not found.",
        )

    return {
        "message": "Clothing deleted successfully!",
    }
