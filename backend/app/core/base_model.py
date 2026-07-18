from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.sql import func

from app.database import Base


class BaseModel(Base):
    """
    Base model inherited by every SQLAlchemy model.
    """

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )