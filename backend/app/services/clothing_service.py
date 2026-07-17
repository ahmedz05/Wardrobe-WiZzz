import os
import uuid

from fastapi import UploadFile

from app.database import SessionLocal
from app.models.clothing import Clothing


def create_clothing(
    user_id: int,
    name: str,
    category: str,
    subcategory: str | None = None,
    color: str | None = None,
    fit: str | None = None,
    material: str | None = None,
    season: str | None = None,
    style: str | None = None,
    brand: str | None = None,
    image_url: str | None = None
):
    db = SessionLocal()

    new_clothing = Clothing(
        user_id=user_id,
        name=name,
        category=category,
        subcategory=subcategory,
        color=color,
        fit=fit,
        material=material,
        season=season,
        style=style,
        brand=brand,
        image_url=image_url
    )

    db.add(new_clothing)
    db.commit()
    db.refresh(new_clothing)
    db.close()

    return new_clothing


def get_user_clothing(user_id: int):
    db = SessionLocal()

    clothes = (
        db.query(Clothing)
        .filter(
            Clothing.user_id == user_id
        )
        .all()
    )

    db.close()

    return clothes


def get_clothing_by_id(
    clothing_id: int,
    user_id: int
):
    db = SessionLocal()

    clothing = (
        db.query(Clothing)
        .filter(
            Clothing.id == clothing_id,
            Clothing.user_id == user_id
        )
        .first()
    )

    db.close()

    return clothing


def update_clothing(
    clothing_id: int,
    user_id: int,
    name: str,
    category: str,
    subcategory: str | None = None,
    color: str | None = None,
    fit: str | None = None,
    material: str | None = None,
    season: str | None = None,
    style: str | None = None,
    brand: str | None = None,
    image_url: str | None = None
):
    db = SessionLocal()

    clothing = (
        db.query(Clothing)
        .filter(
            Clothing.id == clothing_id,
            Clothing.user_id == user_id
        )
        .first()
    )

    if not clothing:
        db.close()
        return None

    clothing.name = name
    clothing.category = category
    clothing.subcategory = subcategory
    clothing.color = color
    clothing.fit = fit
    clothing.material = material
    clothing.season = season
    clothing.style = style
    clothing.brand = brand
    clothing.image_url = image_url

    db.commit()
    db.refresh(clothing)
    db.close()

    return clothing


def delete_clothing(
    clothing_id: int,
    user_id: int
):
    db = SessionLocal()

    clothing = (
        db.query(Clothing)
        .filter(
            Clothing.id == clothing_id,
            Clothing.user_id == user_id
        )
        .first()
    )

    if not clothing:
        db.close()
        return False

    db.delete(clothing)
    db.commit()
    db.close()

    return True


def upload_clothing_image(
    clothing_id: int,
    user_id: int,
    file: UploadFile
):
    db = SessionLocal()

    clothing = (
        db.query(Clothing)
        .filter(
            Clothing.id == clothing_id,
            Clothing.user_id == user_id
        )
        .first()
    )

    if not clothing:
        db.close()
        return None

    uploads_dir = "uploads"

    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    extension = os.path.splitext(file.filename)[1].lower()

    allowed_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    if extension not in allowed_extensions:
        db.close()
        return None

    filename = f"{uuid.uuid4()}{extension}"

    filepath = os.path.join(
        uploads_dir,
        filename
    )

    with open(filepath, "wb") as image:
        image.write(file.file.read())

    clothing.image_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(clothing)
    db.close()

    return clothing