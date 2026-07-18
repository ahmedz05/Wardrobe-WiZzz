from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base_model import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    subcategories = relationship(
        "SubCategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )


class SubCategory(BaseModel):
    __tablename__ = "subcategories"

    name = Column(
        String,
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    category = relationship(
        "Category",
        back_populates="subcategories"
    )

    clothes = relationship(
        "Clothing",
        back_populates="subcategory"
    )