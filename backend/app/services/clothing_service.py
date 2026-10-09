from sqlalchemy.orm import Session

from app.models.clothing import Clothing
from app.models.color import Color
from app.schemas.clothing_schema import ClothingCreate, ClothingUpdate


def create_clothing(
    db: Session,
    user_id: int,
    clothing: ClothingCreate,
):
    clothing_data = clothing.model_dump()

    color_id = clothing_data.get("color_id")

    if color_id is not None:
        color = (
            db.query(Color)
            .filter(
                Color.id == color_id,
                Color.is_active.is_(True),
            )
            .first()
        )

        if not color:
            raise ValueError(
                "The selected color does not exist or is inactive."
            )

    db_clothing = Clothing(
        user_id=user_id,
        **clothing_data,
    )

    db.add(db_clothing)
    db.commit()
    db.refresh(db_clothing)

    return db_clothing


def get_user_clothing(
    db: Session,
    user_id: int,
):
    return (
        db.query(Clothing)
        .filter(
            Clothing.user_id == user_id,
            Clothing.is_active.is_(True),
        )
        .all()
    )


def get_clothing_by_id(
    db: Session,
    clothing_id: int,
    user_id: int,
):
    return (
        db.query(Clothing)
        .filter(
            Clothing.id == clothing_id,
            Clothing.user_id == user_id,
            Clothing.is_active.is_(True),
        )
        .first()
    )


def update_clothing(
    db: Session,
    clothing_id: int,
    user_id: int,
    clothing_data: ClothingUpdate,
):
    clothing = get_clothing_by_id(
        db=db,
        clothing_id=clothing_id,
        user_id=user_id,
    )

    if not clothing:
        return None

    update_data = clothing_data.model_dump(
        exclude_unset=True
    )

    color_id = update_data.get("color_id")

    if color_id is not None:
        color = (
            db.query(Color)
            .filter(
                Color.id == color_id,
                Color.is_active.is_(True),
            )
            .first()
        )

        if not color:
            raise ValueError(
                "The selected color does not exist or is inactive."
            )

    for key, value in update_data.items():
        setattr(
            clothing,
            key,
            value,
        )

    db.commit()
    db.refresh(clothing)

    return clothing


def delete_clothing(
    db: Session,
    clothing_id: int,
    user_id: int,
):
    clothing = get_clothing_by_id(
        db=db,
        clothing_id=clothing_id,
        user_id=user_id,
    )

    if not clothing:
        return None

    db.delete(clothing)
    db.commit()

    return clothing