from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = 'success'
    data: T
    timestamp: datetime


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
