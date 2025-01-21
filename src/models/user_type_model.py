# import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from commonLib.models.base_class import Base
from src.core.settings.configurations.config import settings
from uuid import uuid4

class UserType(Base):
    __tablename__ = "user_types"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="user_type")
    invite_user_type = relationship("UserInvite", back_populates="user_type")

    def __init__(self, name: str):
        self.name = name