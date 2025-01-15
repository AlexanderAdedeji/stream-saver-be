from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel, Field, ValidationError, validator
from src.commonLib.models.mongo_base_class import PyObjectId

# Define a Pydantic model for ObjectId validation
# # Base Pydantic model for MongoDB documents
class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

ModelType = TypeVar("ModelType", bound=MongoBaseModel)

class BaseMongo(Generic[ModelType]):
    def __init__(self, db: AsyncIOMotorDatabase, model: Type[ModelType]):
        self.model = model
        self.collection: AsyncIOMotorCollection = db[model.__collectionname__()]

    async def get(self, object_id: str) -> Optional[ModelType]:
        try:
            obj_id = PyObjectId.validate(object_id)
            document = await self.collection.find_one({"_id": obj_id})
            if document:
                return self.model(**document)
        except (ValidationError, Exception) as e:
            # Log the error
            print(f"Error in get: {e}")
        return None

    async def get_multiple(
        self, conditions: Dict[str, Any] = {}, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        documents = (
            self.collection.find(conditions).skip(skip).limit(limit)
        )
        return [self.model(**doc) async for doc in documents]

    async def create(self, obj_in: BaseModel) -> Optional[ModelType]:
        try:
            obj_in_dict = obj_in.dict(by_alias=True)
            obj_in_dict["created_at"] = datetime.utcnow()
            obj_in_dict["updated_at"] = datetime.utcnow()
            result = await self.collection.insert_one(obj_in_dict)
            return await self.get(str(result.inserted_id))
        except Exception as e:
            # Log the error
            print(f"Error in create: {e}")
        return None

    async def update(
        self, object_id: str, obj_in: Union[BaseModel, Dict[str, Any]]
    ) -> Optional[ModelType]:
        try:
            obj_id = PyObjectId.validate(object_id)
            if isinstance(obj_in, dict):
                update_data = {"$set": obj_in}
            else:
                update_data = {"$set": obj_in.dict(exclude_unset=True)}
            update_data["$set"]["updated_at"] = datetime.utcnow()
            await self.collection.update_one({"_id": obj_id}, update_data)
            return await self.get(object_id)
        except (ValidationError, Exception) as e:
            # Log the error
            print(f"Error in update: {e}")
        return None

    async def delete(self, object_id: str) -> bool:
        try:
            obj_id = PyObjectId.validate(object_id)
            result = await self.collection.delete_one({"_id": obj_id})
            return result.deleted_count > 0
        except (ValidationError, Exception) as e:
            # Log the error
            print(f"Error in delete: {e}")
        return False
