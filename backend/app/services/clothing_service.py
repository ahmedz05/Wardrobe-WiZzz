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