from sqlalchemy.orm import Session

from app.models.material import Material
from app.schemas.material_schema import MaterialCreate


def create_material(
    db: Session,
    material: MaterialCreate
):
    db_material = Material(
        **material.model_dump()
    )

    db.add(db_material)
    db.commit()
    db.refresh(db_material)

    return db_material


def get_all_materials(
    db: Session
):
    return (
        db.query(Material)
        .order_by(Material.name)
        .all()
    )


def get_material(
    db: Session,
    material_id: int
):
    return (
        db.query(Material)
        .filter(
            Material.id == material_id
        )
        .first()
    )


def update_material(
    db: Session,
    material_id: int,
    material_data: MaterialCreate
):
    material = get_material(
        db,
        material_id
    )

    if not material:
        return None

    for key, value in material_data.model_dump().items():
        setattr(
            material,
            key,
            value
        )

    db.commit()
    db.refresh(material)

    return material


def delete_material(
    db: Session,
    material_id: int
):
    material = get_material(
        db,
        material_id
    )

    if not material:
        return None

    db.delete(material)
    db.commit()

    return material