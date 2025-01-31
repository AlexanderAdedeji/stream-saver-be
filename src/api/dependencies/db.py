from typing import Generator
from src.database.sessions.session import SessionLocal, Session
from sqlalchemy.exc import SQLAlchemyError
from src.commonLib.utils.logger_config import logger


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed.")


