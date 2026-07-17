from app.database import SessionLocal
from app.models.category import Category, SubCategory

from app.data.fashion_categories import FASHION_CATEGORIES


def seed_categories():

    db = SessionLocal()

    try:

        for category_name, subcategories in FASHION_CATEGORIES.items():

            existing_category = (
                db.query(Category)
                .filter(
                    Category.name == category_name
                )
                .first()
            )

            if existing_category:

                category = existing_category

            else:

                category = Category(
                    name=category_name
                )

                db.add(category)

                db.commit()

                db.refresh(category)


            for subcategory_name in subcategories:

                existing_subcategory = (
                    db.query(SubCategory)
                    .filter(
                        SubCategory.name == subcategory_name,
                        SubCategory.category_id == category.id
                    )
                    .first()
                )


                if not existing_subcategory:

                    subcategory = SubCategory(
                        name=subcategory_name,
                        category_id=category.id
                    )

                    db.add(subcategory)


        db.commit()

        print("Fashion categories seeded successfully!")


    except Exception as e:

        db.rollback()

        print("Seeding failed:")
        print(e)


    finally:

        db.close()



if __name__ == "__main__":

    seed_categories()