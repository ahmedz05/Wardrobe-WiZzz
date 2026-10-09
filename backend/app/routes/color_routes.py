from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

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

router = APIRouter(
    prefix="/colors",
    tags=["Colors"],
)


@router.post(
    "/",
    response_model=ColorResponse,
)
def create_new_color(
    color: ColorCreate,
    db: Session = Depends(get_db),
):
    return create_color(db, color)


@router.get(
    "/",
    response_model=list[ColorResponse],
)
def get_colors(
    db: Session = Depends(get_db),
):
    return get_all_colors(db)


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


@router.put(
    "/{color_id}",
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


@router.delete(
    "/{color_id}",
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