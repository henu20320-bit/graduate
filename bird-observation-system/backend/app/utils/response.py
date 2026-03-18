from datetime import datetime
from typing import TypeVar

from app.schemas.common import ApiResponse

T = TypeVar('T')


def success_response(data: T, message: str = 'success') -> ApiResponse[T]:
    return ApiResponse[T](success=True, message=message, data=data, timestamp=datetime.utcnow())
