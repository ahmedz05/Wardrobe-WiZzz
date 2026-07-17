from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    height = Column(String)

    weight = Column(String)

    skin_tone = Column(String)

    body_type = Column(String)

    gender = Column(String)

    preferred_styles = Column(String)

    user = relationship(
        "User",
        back_populates="profile"
    )