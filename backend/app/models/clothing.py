from sqlalchemy import Column, Inte r, String, ForeignKey
from app.database import Base


class Clothing(Base):
    __tablename__ = "clothing"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(String, nullable=False)

    category = Column(String, nullable=False)

    color = Column(String)

    season = Column(String)

    style = Column(String)

    brand = Column(String)

    image_url = Column(String)