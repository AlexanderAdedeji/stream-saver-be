import jwt
from datetime import datetime, timedelta
from loguru import logger
from fastapi import HTTPException, status
from pydantic import ValidationError
from src.core.errors.exceptions import InvalidTokenException
from src.core.settings.configurations.config import settings
from src.schemas.jwt_schema import JWTInvite, JWTUser

class JWTService:
    def __init__(
        self,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.JWT_ALGORITHM,
        expire_minutes: int = settings.JWT_EXPIRE_MINUTES,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def decode_token(self, token: str) -> dict:
        """Decode a JWT token and validate its claims."""
        try:
            decoded_payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            if "exp" in decoded_payload and decoded_payload["exp"] <= datetime.utcnow().timestamp():
                raise InvalidTokenException(detail="Token has expired.")
            return decoded_payload
        except jwt.ExpiredSignatureError:
            logger.error("JWT expired.")
            raise InvalidTokenException(detail="Token has expired.")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT: {e}")
            raise InvalidTokenException(detail="Invalid token.")
        except KeyError as e:
            logger.error(f"Missing key in JWT payload: {e}")
            raise InvalidTokenException(detail="Malformed token payload.")

    def generate_token(self, payload: dict, expires_delta: timedelta = None) -> str:
        """Generate a JWT token with optional expiration."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.expire_minutes)

        now = datetime.utcnow()
        payload.update({
            "exp": (now + expires_delta).timestamp(),
            "iat": now.timestamp(),
        })

        logger.debug(f"Generating JWT with payload: {payload}")

        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error encoding JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating token."
            )

    def get_user_id_from_token(self, token: str) -> str:
        """Extract user ID from a JWT token."""
        payload = self.decode_token(token)
        return payload.get("id", None)

    def get_user_email_from_token(self, token: str) -> str:
        """Extract email from a JWT token."""
        payload = self.decode_token(token)
        return payload.get("email", None)

    def generate_invitation_token(self, id: str, expires_delta: timedelta = None) -> str:
        """Generate a JWT token for invitations."""
        jwt_content = JWTInvite(id=id).dict()
        token = self.generate_token(jwt_content, expires_delta)
        return token

    def validate_token_structure(self, token: str) -> None:
        """Validate the basic structure of a JWT token."""
        if not isinstance(token, str) or len(token.split(".")) != 3:
            raise InvalidTokenException(detail="Malformed token structure.")

jwt_service = JWTService()

# Example usage:
# token = jwt_service.generate_token({"id": "123", "email": "user@example.com"})
# payload = jwt_service.decode_token(token)
