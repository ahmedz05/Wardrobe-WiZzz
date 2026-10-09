from sqlalchemy.orm import Session

from app.models.color import Color
from app.schemas.color_schema import (
    ColorCreate,
    ColorUpdate,
)


def create_color(
    db: Session,
    color: ColorCreate,
):
    db_color = Color(
        **color.model_dump()
    )

    db.add(db_color)
    db.commit()
    db.refresh(db_color)

    return db_color


def get_all_colors(
    db: Session,
):
    return (
        db.query(Color)
        .order_by(Color.name)
        .all()
    )


def get_color_by_id(
    db: Session,
    color_id: int,
):
    return (
        db.query(Color)
        .filter(Color.id == color_id)
        .first()
    )


def get_color_by_slug(
    db: Session,
    slug: str,
):
    return (
        db.query(Color)
        .filter(Color.slug == slug)
        .first()
    )


def update_color(
    db: Session,
    color_id: int,
    color_data: ColorUpdate,
):
    color = get_color_by_id(
        db,
        color_id,
    )

    if color is None:
        return None

    update_data = color_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            color,
            field,
            value,
        )

    db.commit()
    db.refresh(color)

    return color


def delete_color(
    db: Session,
    color_id: int,
):
    color = get_color_by_id(
        db,
        color_id,
    )

    if color is None:
        return None

    db.delete(color)
    db.commit()

    return color