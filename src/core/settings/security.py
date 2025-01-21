from passlib.context import CryptContext
from src.core.settings.configurations.config import settings

# Dynamic scheme configuration from settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AppSecurity:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for storing."""
        return pwd_context.hash(password)

    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Check if the password meets strength requirements."""
        return (
            len(password) >= 8 and
            any(c.isdigit() for c in password) and
            any(c.isalpha() for c in password) and
            not password.isalnum()
        )

    @staticmethod
    def generate_reset_token(user_id: str) -> str:
        pass

    @staticmethod
    def verify_reset_token(token: str) -> bool:
        pass


security = AppSecurity()
