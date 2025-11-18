"""
Service layer for flight business logic
"""
from typing import Optional, List, Dict, Any, Tuple
from app.repositories.flight_repository import FlightRepository
from app.models import Flight, FlightFilter, FlightSort, PaginationParams
from app.exceptions import FlightNotFoundError, FlightNumberExistsError, ValidationError


class FlightService:
    """Service for flight business logic"""

    @staticmethod
    def create_flight(flight_data: Flight) -> Dict[str, Any]:
        """Create a new flight"""
        try:
            # model_dump() automatically converts str Enum to string value
            flight_dict = flight_data.model_dump()
            return FlightRepository.create(flight_dict)
        except Exception as e:
            if isinstance(e, (FlightNotFoundError, FlightNumberExistsError)):
                raise
            raise ValidationError(f"Error creating flight: {str(e)}")

    @staticmethod
    def get_flight(flight_id: int) -> Dict[str, Any]:
        """Get a flight by ID"""
        try:
            return FlightRepository.get_by_id(flight_id)
        except FlightNotFoundError:
            raise
        except Exception as e:
            raise ValidationError(f"Error retrieving flight: {str(e)}")

    @staticmethod
    def get_flights(
        filters: Optional[FlightFilter] = None,
        sort: Optional[FlightSort] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Get flights with filtering, sorting, and pagination"""
        try:
            flights, total = FlightRepository.get_all(filters, sort, pagination)
            
            pagination_info = {}
            if pagination:
                total_pages = (total + pagination.page_size - 1) // pagination.page_size
                pagination_info = {
                    'page': pagination.page,
                    'page_size': pagination.page_size,
                    'total': total,
                    'total_pages': total_pages
                }
            else:
                pagination_info = {
                    'page': 1,
                    'page_size': total,
                    'total': total,
                    'total_pages': 1
                }
            
            return flights, pagination_info
        except Exception as e:
            raise ValidationError(f"Error retrieving flights: {str(e)}")

    @staticmethod
    def update_flight(flight_id: int, update_data: Flight) -> Dict[str, Any]:
        """Update a flight"""
        try:
            # Remove None values
            update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
            
            if not update_dict:
                raise ValidationError("No fields to update")
            
            return FlightRepository.update(flight_id, update_dict)
        except FlightNotFoundError:
            raise
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Error updating flight: {str(e)}")

    @staticmethod
    def delete_flight(flight_id: int) -> bool:
        """Delete a flight"""
        try:
            return FlightRepository.delete(flight_id)
        except FlightNotFoundError:
            raise
        except Exception as e:
            raise ValidationError(f"Error deleting flight: {str(e)}")

