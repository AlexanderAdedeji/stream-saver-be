from typing import Any, Dict
from datetime import datetime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, DateTime, Integer
from fastapi.encoders import jsonable_encoder

@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_json(self) -> Dict[str, Any]:
        return jsonable_encoder(self)

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

# Example model using the Base and TimestampMixin
class MyModel(TimestampMixin, Base):
    id = Column(Integer, primary_key=True, index=True)
    # Add other model-specific fields here
