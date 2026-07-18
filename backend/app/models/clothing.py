from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class Clothing(BaseModel):
    __tablename__ = "clothing"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    subcategory_id = Column(
        Integer,
        ForeignKey("subcategories.id"),
        nullable=True
    )

    color = Column(String)

    fit = Column(String)

    material = Column(String)

    season = Column(String)

    style = Column(String)

    brand = Column(String)

    silhouette = Column(String)

    layering_role = Column(String)

    warmth_level = Column(String)

    occasion = Column(String)

    image_url = Column(String)

    owner = relationship(
        "User",
        back_populates="clothes"
    )

    subcategory = relationship(
        "SubCategory",
        back_populates="clothes"
    )