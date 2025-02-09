from pydantic_settings import BaseSettings
from pydantic import Field
import os




class CustomSettings(BaseSettings):
    # General Settings
    ALLOWED_HOSTS: str = Field(..., description="Comma-separated list of allowed hosts")
    ALLOWED_ORIGINS: str = Field(
        ..., description="Comma-separated list of allowed CORS origins"
    )
    ALLOWED_METHODS: str = Field(
        ..., description="Comma-separated list of allowed HTTP methods"
    )
    SECRET_KEY: str = Field(
        ..., env="SECRET_KEY", description="Secret key for the application"
    )
    RESET_TOKEN_EXPIRE_MINUTES: int = Field(
        60, description="Reset token expiration time in minutes"
    )
    PROJECT_NAME: str = Field(..., description="Project name")
    API_URL_PREFIX: str = Field(..., description="API URL prefix")
    VERSION: str = Field("0.1.0", description="API version")
    DEBUG: bool = Field(False, description="Debug mode")

    # Database Settings
    POSTGRES_DB_URL: str = Field(
        ..., env="POSTGRES_DB_URL", description="PostgreSQL database URL"
    )
    MONGO_DB_URL: str = Field(
        ..., env="MONGO_DB_URL", description="MongoDB database URL"
    )
    MONGO_DB_NAME: str = Field(
        ..., env="MONGO_DB_NAME", description="MongoDB database name"
    )

    # JWT and Security Settings
    JWT_TOKEN_PREFIX: str = Field(..., description="Prefix for JWT tokens")
    JWT_ALGORITHM: str = Field(..., description="Algorithm used for JWT tokens")
    JWT_EXPIRE_MINUTES: int = Field(..., description="JWT token expiration in minutes")
    HEADER_KEY: str = Field(..., description="Header key for authentication")
    API_KEY_AUTH_ENABLED: bool = Field(
        True, description="Enable or disable API key authentication"
    )
    INSTAGRAM_SESSION_ID:str

    # Email Configuration

    # User Types



    # Payment Configuration


    class Config:
        env_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "env_files", ".env"
        )
        env_file_encoding = "utf-8"



settings = CustomSettings()
