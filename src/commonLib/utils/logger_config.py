from typing import Optional
from loguru import logger
import sys
from pathlib import Path
import os

class LoggerConfig:
    def __init__(self, log_dir: Optional[str] = None, log_file: str = "app.log"):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.log_dir = Path(log_dir) if log_dir else self.project_root / "logs"
        self.log_file_path = self.log_dir / log_file

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._configure_logger()

    def _configure_logger(self):
        try:
            logger.remove()  # Remove default handlers
            
            # Console Logging (for real-time debugging)
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{process}</cyan>:<cyan>{thread}</cyan> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                       "<level>{message}</level>",
                level=os.getenv("LOG_LEVEL", "INFO"),
                colorize=True,
            )

            # General Application Logs
            logger.add(
                self.log_file_path,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {process}:{thread} | {name}:{function}:{line} - {message}",
                rotation=os.getenv("LOG_ROTATION", "10 MB"),
                retention=os.getenv("LOG_RETENTION", "10 days"),
                compression=os.getenv("LOG_COMPRESSION", "zip"),
                level=os.getenv("LOG_FILE_LEVEL", "INFO"),
            )

            # Error Logs
            logger.add(
                self.log_dir / "error.log",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
                rotation="5 MB",
                retention="7 days",
                compression="zip",
                level="ERROR",
            )

            # Debug Logs
            logger.add(
                self.log_dir / "debug.log",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
                rotation="5 MB",
                retention="7 days",
                compression="zip",
                level="DEBUG",
            )

         
            logger.add(
                self.log_dir / "app.json",
                serialize=True,
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                level="INFO",
            )

        except Exception as e:
            logger.error(f"Failed to configure logger: {e}")


LoggerConfig()

logger = logger
