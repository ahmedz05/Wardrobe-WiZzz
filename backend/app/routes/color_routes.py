from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_dependencies import require_catalog_write_access

from app.schemas.color_schema import (
    ColorCreate,
    ColorUpdate,
    ColorResponse,
)

from app.services.color_service import (
    create_color,
    get_all_colors,
    get_color_by_id,
    update_color,
    delete_color,
)

from app.services.color_matching_service import (
    evaluate_color_pair,
    rank_color_matches,
)


router = APIRouter(
    prefix="/colors",
    tags=["Colors"],
)


# -------------------------
# CREATE COLOR
# -------------------------

@router.post(
    "/",
    dependencies=[Depends(require_catalog_write_access)],
    response_model=ColorResponse,
)
def create_new_color(
    color: ColorCreate,
    db: Session = Depends(get_db),
):
    return create_color(
        db,
        color,
    )


# -------------------------
# GET ALL COLORS
# -------------------------

@router.get(
    "/",
    response_model=list[ColorResponse],
)
def get_colors(
    db: Session = Depends(get_db),
):
    return get_all_colors(db)


# -------------------------
# COMPARE TWO COLORS
# -------------------------

@router.get("/compare")
def compare_colors(
    color_1_id: int,
    color_2_id: int,
    db: Session = Depends(get_db),
):
    first_color = get_color_by_id(
        db,
        color_1_id,
    )

    second_color = get_color_by_id(
        db,
        color_2_id,
    )

    if first_color is None:
        raise HTTPException(
            status_code=404,
            detail="First color not found.",
        )

    if second_color is None:
        raise HTTPException(
            status_code=404,
            detail="Second color not found.",
        )

    try:
        return evaluate_color_pair(
            first_color,
            second_color,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# -------------------------
# GET BEST COLOR MATCHES
# -------------------------

@router.get("/{color_id}/matches")
def get_color_matches(
    color_id: int,
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
    db: Session = Depends(get_db),
):
    base_color = get_color_by_id(
        db,
        color_id,
    )

    if base_color is None:
        raise HTTPException(
            status_code=404,
            detail="Color not found.",
        )

    if not base_color.is_active:
        raise HTTPException(
            status_code=400,
            detail="Color is inactive.",
        )

    colors = get_all_colors(db)

    matches = rank_color_matches(
        base_color=base_color,
        colors=colors,
        limit=limit,
    )

    return {
        "base_color": {
            "id": base_color.id,
            "name": base_color.name,
            "hex_code": base_color.hex_code,
            "color_family": base_color.color_family,
            "undertone": base_color.undertone,
            "brightness": base_color.brightness,
            "saturation": base_color.saturation,
            "is_neutral": base_color.is_neutral,
        },
        "matches": matches,
    }


# -------------------------
# GET COLOR BY ID
# -------------------------

@router.get(
    "/{color_id}",
    response_model=ColorResponse,
)
def get_color(
    color_id: int,
    db: Session = Depends(get_db),
):
    color = get_color_by_id(
        db,
        color_id,
    )

    if color is None:
        raise HTTPException(
            status_code=404,
            detail="Color not found",
        )

    return color


# -------------------------
# UPDATE COLOR
# -------------------------

@router.put(
    "/{color_id}",
    dependencies=[Depends(require_catalog_write_access)],
    response_model=ColorResponse,
)
def update_existing_color(
    color_id: int,
    color: ColorUpdate,
    db: Session = Depends(get_db),
):
    updated = update_color(
        db,
        color_id,
        color,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Color not found",
        )

    return updated


# -------------------------
# DELETE COLOR
# -------------------------

@router.delete(
    "/{color_id}",
    dependencies=[Depends(require_catalog_write_access)],
)
def remove_color(
    color_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_color(
        db,
        color_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Color not found",
        )

    return {
        "message": "Color deleted successfully"
    }
