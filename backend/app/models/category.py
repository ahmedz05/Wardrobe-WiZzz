from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        unique=True,
        nullable=False
    )

    subcategories = relationship(
        "SubCategory",
        back_populates="category"
    )


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

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