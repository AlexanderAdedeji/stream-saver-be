from pydantic import BaseModel
from typing import Optional, Dict, Any, TypeVar, Generic

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: Optional[T] = None
    metadata: Optional[Dict[str, Any]] = None

def create_response(
    message: str = "",
    status_code: int = 200,
    data: Optional[T] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> APIResponse[T]:
    return APIResponse[T](message=message, status_code=status_code, data=data, metadata=metadata)
