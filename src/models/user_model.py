import jwt
from datetime import datetime, timedelta
from uuid import uuid4
from src.commonLib.utils.logger_config import logger
from sqlalchemy import Integer, Column, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship, Session
from commonLib.models.base_class import Base
from src.core.settings import security
from src.schemas.jwt_schema import JWTEMAIL, JWTUser
from src.core.settings.configurations.config import settings



JWT_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES
JWT_ALGORITHM = settings.JWT_ALGORITHM
RESET_TOKEN_EXPIRE_MINUTES = settings.RESET_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY
SUPERUSER_USER_TYPE = settings.SUPERUSER_USER_TYPE


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    hashed_password = Column(String, nullable=False)
    @property
    def set_password(self, password: str) -> None:
        self.hashed_password = security.get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return security.verify_password(password, self.hashed_password)

    def generate_jwt(self, expires_delta: timedelta = None):
        if not self.is_active:
            raise Exception("user is not active")

        jwt_content = JWTUser(id=self.id).dict()
        if expires_delta is None:
            expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)

        now = datetime.now()
        expires_at = now + expires_delta

        jwt_content["exp"] = expires_at.timestamp()
        jwt_content["iat"] = now.timestamp()

        encoded_token = jwt.encode(
            payload=jwt_content, key=str(SECRET_KEY), algorithm=JWT_ALGORITHM
        )
        return encoded_token

    def generate_verification_token(
        self, expires_delta: timedelta = None, **kwargs
    ) -> str:
        """Generate JSON Web Token for a user"""

        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        now = datetime.now()
        expires_at = now + expires_delta
        jwt_content = JWTEMAIL(email=self.email).dict()
        jwt_content.update(kwargs)
        jwt_content.update({"exp": expires_at.timestamp(), "iat": now.timestamp()})
        logger.info(jwt_content)
        encoded_token = jwt.encode(
            payload=jwt_content, key=str(SECRET_KEY), algorithm=JWT_ALGORITHM
        )
        return encoded_token

    def generate_password_reset_token(
        self, db: Session, expires_delta: timedelta = None
    ) -> PasswordResetToken:
        token = security.generate_reset_token(self.email)
        if expires_delta is None:
            expires_delta = timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

        reset_token = reset_token_repo.create(
            db,
            obj_in=ResetTokenCreate(
                user_id=self.id, token=token, expires_at=datetime.now() + expires_delta
            ),
        )

        return reset_token

    def __init__(self, first_name: str, last_name: str, email: str):
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
