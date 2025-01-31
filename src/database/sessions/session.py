from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from src.core.settings.configurations.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = settings.POSTGRES_DB_URL


# Retry configuration for establishing the database connection
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),  
    reraise=True, 
)
def get_engine():
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,  
            pool_pre_ping=True,  
            pool_recycle=1800, 
            connect_args={"sslmode": "require"},
        )
        logger.info("Successfully created PostgreSQL engine.")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Error creating PostgreSQL engine: {e}")
        raise


# Create the SQLAlchemy engine
engine = get_engine()

# SessionLocal factory for creating new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
