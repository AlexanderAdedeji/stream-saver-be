from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from src.core.settings.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = settings.POSTGRES_DB_URL


# Retry configuration for establishing the database connection
@retry(
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    reraise=True,  # Raise the last exception if all retries fail
)
def get_engine():
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,  # Increased timeout for better resilience
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=1800,  # Recycle connections after 30 minutes
            connect_args={"sslmode": "require"},  # Enforce SSL for secure communication
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
