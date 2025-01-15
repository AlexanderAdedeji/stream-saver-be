from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class MongoBase(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Document creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Document update timestamp")

    @classmethod
    def __collectionname__(cls) -> str:
        return cls.__name__.lower()

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
