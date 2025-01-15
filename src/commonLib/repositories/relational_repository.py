from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from commonLib.models.base_class import Base as BaseDeclarativeClass

ModelType = TypeVar("ModelType", bound=BaseDeclarativeClass)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def exists(self, db: Session, id: Any) -> bool:
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_multi_by_ids(self, db: Session, *, ids: List[Any]) -> List[ModelType]:
        return db.query(self.model).filter(self.model.id.in_(ids)).all()

    def get_all(self, db: Session) -> List[ModelType]:
        return db.query(self.model).all()

    def get_count(self, db: Session) -> int:
        return db.query(self.model).count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity issue.",
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def get_by_field(
        self, db: Session, *, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        return db.query(self.model).filter(getattr(self.model, field_name) == field_value).first()

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity issue.",
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def remove(self, db: Session, *, id: Any) -> ModelType:
        obj = db.query(self.model).get(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found.",
            )
        try:
            db.delete(obj)
            db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    def get_paginated(
        self, db: Session, *, skip: int = 0, limit: int = 10
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_paginated_with_filter(
        self,
        db: Session,
        *,
        filter_conditions: Dict[str, Any],
        skip: int = 0,
        limit: int = 10
    ) -> List[ModelType]:
        query = db.query(self.model)
        for field, value in filter_conditions.items():
            query = query.filter(getattr(self.model, field) == value)
        return query.offset(skip).limit(limit).all()
