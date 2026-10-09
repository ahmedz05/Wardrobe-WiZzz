from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class Material(BaseModel):
    __tablename__ = "materials"

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    slug = Column(
        String,
        unique=True,
        nullable=False
    )

    material_type = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    care_instructions = Column(
        Text,
        nullable=True
    )

    is_natural = Column(
        Boolean,
        nullable=False,
        default=False
    )

    clothing_items = relationship(
        "Clothing",
        back_populates="material"
    )