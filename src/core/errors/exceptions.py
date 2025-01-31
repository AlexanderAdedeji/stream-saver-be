from typing import Optional, Any
from src.core.errors import error_strings
from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from src.commonLib.utils.logger_config import logger


class BaseCustomException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Optional[str] = None,
        default_detail: str = "",
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        message = detail or default_detail
        logger.error(f"Exception raised: {message} (Status Code: {status_code})")
        super().__init__(status_code=status_code, detail=message, headers=headers)


class ServerException(BaseCustomException):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            default_detail=error_strings.SERVER_ERROR,
        )


class IncorrectLoginException(BaseCustomException):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail,
            default_detail=error_strings.INCORRECT_LOGIN_INPUT,
        )


class DisallowedLoginException(BaseCustomException):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=detail,
            default_detail=error_strings.UNVERIFIED_USER_ERROR,
        )


class AlreadyExistsException(BaseCustomException):
    def __init__(self, entity_name: str, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_409_CONFLICT,
            detail=detail or error_strings.ALREADY_EXISTS.format(entity_name),
        )


class InvalidTokenException(BaseCustomException):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail=detail,
            default_detail=error_strings.MALFORMED_PAYLOAD,
        )


class ObjectNotFoundException(BaseCustomException):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            detail=detail,
            default_detail=error_strings.NOT_FOUND,
        )


class UnauthorizedEndpointException(BaseCustomException):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail=detail,
            default_detail=error_strings.UNAUTHORIZED_ACTION,
        )


class DoesNotExistException(BaseCustomException):
    def __init__(self, entity_name: str, detail: Optional[str] = None) -> None:
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            detail=detail or error_strings.DOES_NOT_EXIST.format(entity_name),
        )
