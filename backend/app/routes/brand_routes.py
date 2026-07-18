from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.brand_schema import (
    BrandCreate,
    BrandResponse,
)

from app.services.brand_service import (
    create_brand,
    get_all_brands,
    get_brand,
)

router = APIRouter(
    prefix="/brands",
    tags=["Brands"]
)


@router.post(
    "/",
    response_model=BrandResponse
)
def create_new_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db)
):
    return create_brand(
        db,
        brand
    )


@router.get(
    "/",
    response_model=list[BrandResponse]
)
def read_brands(
    db: Session = Depends(get_db)
):
    return get_all_brands(db)


@router.get(
    "/{brand_id}",
    response_model=BrandResponse
)
def read_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    brand = get_brand(
        db,
        brand_id
    )

    if brand is None:
        raise HTTPException(
            status_code=404,
            detail="Brand not found"
        )

    return brand