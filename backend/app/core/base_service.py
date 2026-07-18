from typing import Generic, Type, TypeVar
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Generic CRUD service for SQLAlchemy models.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, item_id: int):
        return (
            db.query(self.model)
            .filter(self.model.id == item_id)
            .first()
        )

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def delete(self, db: Session, item_id: int):
        obj = self.get(db, item_id)

        if obj:
            db.delete(obj)
            db.commit()

        return obj