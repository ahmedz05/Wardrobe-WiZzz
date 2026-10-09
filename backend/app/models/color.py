from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class Color(BaseModel):
    __tablename__ = "colors"

    name = Column(
        String,
        unique=True,
        nullable=False,
    )

    slug = Column(
        String,
        unique=True,
        nullable=False,
    )

    hex_code = Column(
        String,
        nullable=False,
    )

    rgb_value = Column(
        String,
        nullable=True,
    )

    color_family = Column(
        String,
        nullable=False,
    )

    undertone = Column(
        String,
        nullable=True,
    )

    brightness = Column(
        String,
        nullable=True,
    )

    saturation = Column(
        String,
        nullable=True,
    )

    description = Column(
        String,
        nullable=True,
    )

    is_neutral = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    clothing_items = relationship(
        "Clothing",
        back_populates="color",
    )