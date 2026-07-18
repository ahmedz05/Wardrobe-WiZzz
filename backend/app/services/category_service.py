from app.database import SessionLocal

from app.models.category import Category, SubCategory


def get_all_categories():

    db = SessionLocal()

    categories = (
        db.query(Category)
        .all()
    )

    db.close()

    return categories



def get_category_subcategories(category_id: int):

    db = SessionLocal()

    category = (
        db.query(Category)
        .filter(
            Category.id == category_id
        )
        .first()
    )

    if not category:
        db.close()
        return None


    subcategories = (
        db.query(SubCategory)
        .filter(
            SubCategory.category_id == category_id
        )
        .all()
    )

    db.close()


    return {
        "category": category.name,
        "subcategories": [
            sub.name
            for sub in subcategories
        ]
    }