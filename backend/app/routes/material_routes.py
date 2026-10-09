from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.material_schema import (
    MaterialCreate,
    MaterialResponse
)
from app.services.material_service import (
    create_material,
    get_all_materials,
    get_material,
    update_material,
    delete_material
)

router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)


@router.post(
    "/",
    response_model=MaterialResponse
)
def create_new_material(
    material: MaterialCreate,
    db: Session = Depends(get_db)
):
    return create_material(
        db,
        material
    )


@router.get(
    "/",
    response_model=list[MaterialResponse]
)
def read_all_materials(
    db: Session = Depends(get_db)
):
    return get_all_materials(db)


@router.get(
    "/{material_id}",
    response_model=MaterialResponse
)
def read_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = get_material(
        db,
        material_id
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    return material


@router.put(
    "/{material_id}",
    response_model=MaterialResponse
)
def edit_material(
    material_id: int,
    material: MaterialCreate,
    db: Session = Depends(get_db)
):
    updated_material = update_material(
        db,
        material_id,
        material
    )

    if not updated_material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    return updated_material


@router.delete(
    "/{material_id}"
)
def remove_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = delete_material(
        db,
        material_id
    )

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    return {
        "message": "Material deleted successfully"
    }