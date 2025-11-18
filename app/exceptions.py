"""
Custom exceptions for the application
"""
from typing import Optional


class FlightNotFoundError(Exception):
    """Raised when a flight is not found"""
    def __init__(self, flight_id: Optional[int] = None, message: Optional[str] = None):
        self.flight_id = flight_id
        self.message = message or f"Flight with id {flight_id} not found"
        super().__init__(self.message)


class FlightNumberExistsError(Exception):
    """Raised when trying to create a flight with an existing flight number"""
    def __init__(self, flight_number: str):
        self.flight_number = flight_number
        self.message = f"Flight number {flight_number} already exists"
        super().__init__(self.message)


class ValidationError(Exception):
    """Raised when validation fails"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

