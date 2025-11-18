"""
Router for flight endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.flight_service import FlightService
from app.models import Flight, FlightFilter, FlightSort, PaginationParams, FlightResponse
from app.schemas import APIResponse, PaginatedResponse
from app.exceptions import FlightNotFoundError, FlightNumberExistsError, ValidationError

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("", response_model=APIResponse[FlightResponse], status_code=201)
async def create_flight(flight: Flight):
    """Create a new flight"""
    try:
        flight_data = FlightService.create_flight(flight)
        return APIResponse(
            status="success",
            message="Flight created successfully",
            data=FlightResponse(**flight_data)
        )
    except FlightNumberExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=PaginatedResponse[FlightResponse])
async def get_flights(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    origin: Optional[str] = Query(default=None, description="Filter by origin airport"),
    destination: Optional[str] = Query(default=None, description="Filter by destination airport"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    aircraft_type: Optional[str] = Query(default=None, description="Filter by aircraft type"),
    min_seats_available: Optional[int] = Query(default=None, ge=0, description="Minimum available seats"),
    max_seats_available: Optional[int] = Query(default=None, ge=0, description="Maximum available seats"),
    sort_field: str = Query(default="flight_id", description="Field to sort by"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="Sort order")
):
    """Get flights with pagination, filtering, and sorting"""
    try:
        filters = FlightFilter(
            origin=origin,
            destination=destination,
            status=status,
            aircraft_type=aircraft_type,
            min_seats_available=min_seats_available,
            max_seats_available=max_seats_available
        )
        
        sort = FlightSort(field=sort_field, order=sort_order)
        pagination = PaginationParams(page=page, page_size=page_size)
        
        flights, pagination_info = FlightService.get_flights(filters, sort, pagination)
        
        return PaginatedResponse(
            status="success",
            message="Flights retrieved successfully",
            data=[FlightResponse(**flight) for flight in flights],
            pagination=pagination_info
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{flight_id}", response_model=APIResponse[FlightResponse])
async def get_flight(flight_id: int):
    """Get a flight by ID"""
    try:
        flight_data = FlightService.get_flight(flight_id)
        return APIResponse(
            status="success",
            message="Flight retrieved successfully",
            data=FlightResponse(**flight_data)
        )
    except FlightNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{flight_id}", response_model=APIResponse[FlightResponse])
async def update_flight(flight_id: int, flight_update: Flight):
    """Update a flight"""
    try:
        flight_data = FlightService.update_flight(flight_id, flight_update)
        return APIResponse(
            status="success",
            message="Flight updated successfully",
            data=FlightResponse(**flight_data)
        )
    except FlightNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FlightNumberExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{flight_id}", response_model=APIResponse[dict])
async def delete_flight(flight_id: int):
    """Delete a flight"""
    try:
        FlightService.delete_flight(flight_id)
        return APIResponse(
            status="success",
            message="Flight deleted successfully",
            data={"flight_id": flight_id}
        )
    except FlightNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

