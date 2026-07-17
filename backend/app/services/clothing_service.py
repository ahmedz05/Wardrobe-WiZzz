from app.database import SessionLocal
from app.models.clothing import Clothing


def create_clothing(
    user_id: int,
    name: str,
    category: str,
    color: str,
    season: str,
    style: str,
    brand: str,
    image_url: str
):
    db = SessionLocal()

    new_clothing = Clothing(
        user_id=user_id,
        name=name,
        category=category,
        color=color,
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
        .filter(Clothing.user_id == user_id)
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
    color: str,
    season: str,
    style: str,
    brand: str,
    image_url: str
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
    clothing.color = color
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