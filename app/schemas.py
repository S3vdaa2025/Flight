"""
Response schemas for standardized API responses
"""
from typing import Optional, Any, Generic, TypeVar, List, Dict
from pydantic import BaseModel, Field

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response structure"""
    status: str = Field(default="success", description="Response status")
    message: str = Field(default="", description="Response message")
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response structure"""
    status: str = Field(default="success", description="Response status")
    message: str = Field(default="", description="Response message")
    data: List[T] = Field(default_factory=list, description="List of items")
    pagination: Dict[str, Any] = Field(default_factory=dict, description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Data retrieved successfully",
                "data": [],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total": 0,
                    "total_pages": 0
                }
            }
        }

