from typing import Generic, Optional, Dict, Any, TypeVar
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypeVarTuple

T = TypeVar("T")

class GenericResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message: str
    status_code: int
    data: Optional[T] = None
    metadata: Optional[Dict[str, Any]] = None

def create_response(
    message: str = "",
    status_code: int = 200,
    data: Optional[T] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> GenericResponse[T]:
    return GenericResponse[T](message=message, status_code=status_code, data=data, metadata=metadata)
