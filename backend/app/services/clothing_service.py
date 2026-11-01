
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.clothing import Clothing
from app.models.color import Color
from app.schemas.clothing_schema import ClothingCreate, ClothingUpdate


# =====================================
# CREATE CLOTHING
# =====================================

def create_clothing(
    db: Session,
    user_id: int,
    clothing: ClothingCreate,
):
    clothing_data = clothing.model_dump()

    color_id = clothing_data.get("color_id")

    # Validate the selected color.
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

    # Save the new clothing item.
    try:
        db.add(db_clothing)
        db.commit()

    except SQLAlchemyError:
        # Recover the session if the write fails.
        db.rollback()
        raise

    db.refresh(db_clothing)

    return db_clothing


# =====================================
# GET USER CLOTHING
# =====================================

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


# =====================================
# GET CLOTHING BY ID
# =====================================

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


# =====================================
# UPDATE CLOTHING
# =====================================

def update_clothing(
    db: Session,
    clothing_id: int,
    user_id: int,
    clothing_data: ClothingUpdate,
):
    # Find the clothing item belonging to this user.
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

    # Validate the selected color.
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

    # Apply the updated values.
    for key, value in update_data.items():
        setattr(
            clothing,
            key,
            value,
        )

    # Commit the update safely.
    try:
        db.commit()

    except SQLAlchemyError:
        # Discard changes from the failed transaction.
        db.rollback()
        raise

    db.refresh(clothing)

    return clothing


# =====================================
# DELETE CLOTHING
# =====================================

def delete_clothing(
    db: Session,
    clothing_id: int,
    user_id: int,
):
    # Locate only clothing owned by this user.
    clothing = get_clothing_by_id(
        db=db,
        clothing_id=clothing_id,
        user_id=user_id,
    )

    if not clothing:
        return None

    # Delete the item safely.
    try:
        db.delete(clothing)
        db.commit()

    except SQLAlchemyError:
        # Recover the session on database failure.
        db.rollback()
        raise

    return clothing
