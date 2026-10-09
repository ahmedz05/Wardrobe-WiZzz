from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class Clothing(BaseModel):
    __tablename__ = "clothing"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )

    subcategory_id = Column(
        Integer,
        ForeignKey("subcategories.id"),
        nullable=True,
    )

    brand_id = Column(
        Integer,
        ForeignKey("brands.id"),
        nullable=True,
    )

    material_id = Column(
        Integer,
        ForeignKey("materials.id"),
        nullable=True,
    )

    color_id = Column(
        Integer,
        ForeignKey("colors.id"),
        nullable=True,
    )

    season = Column(String)
    style = Column(String)
    fit = Column(String)
    silhouette = Column(String)
    layering_role = Column(String)
    warmth_level = Column(String)
    occasion = Column(String)

    image_url = Column(String)

    # Clothing Metadata
    condition = Column(String)

    favorite = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    purchase_date = Column(Date)

    purchase_price = Column(
        Float,
        default=0.0,
    )

    currency = Column(String)

    last_worn = Column(Date)

    times_worn = Column(
        Integer,
        default=0,
        nullable=False,
    )

    notes = Column(Text)

    owner = relationship(
        "User",
        back_populates="clothes",
    )

    subcategory = relationship(
        "SubCategory",
        back_populates="clothes",
    )

    brand = relationship(
        "Brand",
        back_populates="clothing_items",
    )

    material = relationship(
        "Material",
        back_populates="clothing_items",
    )

    color = relationship(
        "Color",
        back_populates="clothing_items",
    )