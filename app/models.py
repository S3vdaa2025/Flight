"""
Pydantic models for request/response validation
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, model_validator, field_validator


class FlightStatus(str, Enum):
    """Flight status enumeration"""
    SCHEDULED = "scheduled"
    DEPARTED = "departed"
    ARRIVED = "arrived"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class Flight(BaseModel):
    """Base flight model with common fields"""
    flight_number: str = Field(..., min_length=1, max_length=20, description="Flight number")
    origin: str = Field(..., min_length=3, max_length=3, description="Origin airport code")
    destination: str = Field(..., min_length=3, max_length=3, description="Destination airport code")
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    duration_minutes: int = Field(..., ge=0, description="Flight duration in minutes")
    aircraft_type: str = Field(..., min_length=1, max_length=50, description="Aircraft type")
    seats_total: int = Field(..., gt=0, description="Total number of seats")
    seats_available: int = Field(..., ge=0, description="Available seats")
    status: FlightStatus = Field(..., description="Flight status")
    process_id: str = Field(..., min_length=1, max_length=20, description="Process ID")

    @model_validator(mode='after')
    def validate_seats_and_times(self):
        """Validate seats and arrival time"""
        if self.seats_available > self.seats_total:
            raise ValueError('seats_available cannot exceed seats_total')
        # Allow equal times only if duration is 0, otherwise arrival must be after departure
        if self.duration_minutes == 0:
            if self.arrival_time < self.departure_time:
                raise ValueError('arrival_time cannot be before departure_time when duration is 0')
        else:
            if self.arrival_time <= self.departure_time:
                raise ValueError('arrival_time must be after departure_time when duration > 0')
        return self



class FlightResponse(Flight):
    """Model for flight response"""
    flight_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FlightFilter(BaseModel):
    """Model for filtering flights"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    status: Optional[FlightStatus] = None
    aircraft_type: Optional[str] = None
    min_seats_available: Optional[int] = Field(None, ge=0)
    max_seats_available: Optional[int] = Field(None, ge=0)


class FlightSort(BaseModel):
    """Model for sorting flights"""
    field: str = Field(default="flight_id", description="Field to sort by")
    order: str = Field(default="asc", description="Sort order: asc or desc")
    
    @field_validator('order')
    @classmethod
    def validate_order(cls, v):
        """Validate sort order"""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('order must be either "asc" or "desc"')
        return v.lower()


class PaginationParams(BaseModel):
    """Model for pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Number of items per page")

