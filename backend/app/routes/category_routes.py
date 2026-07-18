from fastapi import APIRouter, HTTPException

from app.services.category_service import (
    get_all_categories,
    get_category_subcategories
)


router = APIRouter()



# -------------------------
# GET ALL CATEGORIES
# -------------------------

@router.get("/categories")
def categories():

    return get_all_categories()



# -------------------------
# GET CATEGORY SUBCATEGORIES
# -------------------------

@router.get("/categories/{category_id}/subcategories")
def category_subcategories(
    category_id: int
):

    result = get_category_subcategories(
        category_id
    )


    if not result:

        raise HTTPException(
            status_code=404,
            detail="Category not found."
        )


    return result