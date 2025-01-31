from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from pymongo import MongoClient
from typing import Optional
from src.commonLib.models.mongo_base_class import BaseModel

from src.core.settings.configurations.config import settings
# MongoDB setup
client = MongoClient(settings.MONGO_DB_URL)  
db = client.streamsaver_db
visits_collection = db.visitor_logs




class VisitorLog(BaseModel):
    ip: str = Field(..., description="Visitor's IP Address")
    user_agent: Optional[str] = Field(None, description="User's browser and device details")
    referrer: Optional[HttpUrl] = Field(None, description="URL of the referring page")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Visit timestamp")
