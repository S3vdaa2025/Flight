"""
Tests for flight endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.database import init_db, DATABASE_PATH
import os

# Initialize test database
if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)
init_db()

client = TestClient(app)


@pytest.fixture
def sample_flight_data():
    """Sample flight data for testing"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "flight_number": f"TEST{unique_id}",
        "origin": "JED",
        "destination": "THR",
        "departure_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "arrival_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        "duration_minutes": 120,
        "aircraft_type": "A320",
        "seats_total": 150,
        "seats_available": 100,
        "status": "scheduled",
        "process_id": f"P-TEST-{unique_id}"
    }


def test_create_flight(sample_flight_data):
    """Test creating a new flight"""
    response = client.post("/flights", json=sample_flight_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Flight created successfully"
    assert data["data"]["flight_number"] == sample_flight_data["flight_number"]
    assert data["data"]["flight_id"] is not None


def test_get_flight_by_id(sample_flight_data):
    """Test getting a flight by ID"""
    # First create a flight
    create_response = client.post("/flights", json=sample_flight_data)
    assert create_response.status_code == 201
    flight_id = create_response.json()["data"]["flight_id"]
    
    # Then get it
    response = client.get(f"/flights/{flight_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["flight_id"] == flight_id
    assert data["data"]["flight_number"] == sample_flight_data["flight_number"]


def test_get_flights_with_pagination():
    """Test getting flights with pagination"""
    response = client.get("/flights?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 5


def test_get_flights_with_filtering():
    """Test getting flights with filtering"""
    response = client.get("/flights?origin=JED&status=scheduled")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Verify all returned flights match the filter
    for flight in data["data"]:
        assert flight["origin"] == "JED"
        assert flight["status"] == "scheduled"


def test_get_flights_with_sorting():
    """Test getting flights with sorting"""
    response = client.get("/flights?sort_field=departure_time&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Verify flights are sorted (if there are multiple flights)
    if len(data["data"]) > 1:
        times = [flight["departure_time"] for flight in data["data"]]
        assert times == sorted(times, reverse=True)


def test_update_flight(sample_flight_data):
    """Test updating a flight"""
    # First create a flight
    create_response = client.post("/flights", json=sample_flight_data)
    assert create_response.status_code == 201
    flight_id = create_response.json()["data"]["flight_id"]
    
    # Update it - need to provide all required fields since Flight is used
    update_data = sample_flight_data.copy()
    update_data["status"] = "departed"
    update_data["seats_available"] = 90
    response = client.put(f"/flights/{flight_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "departed"
    assert data["data"]["seats_available"] == 90


def test_delete_flight(sample_flight_data):
    """Test deleting a flight"""
    # First create a flight
    create_response = client.post("/flights", json=sample_flight_data)
    assert create_response.status_code == 201
    flight_id = create_response.json()["data"]["flight_id"]
    
    # Delete it
    response = client.delete(f"/flights/{flight_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["flight_id"] == flight_id
    
    # Verify it's deleted
    get_response = client.get(f"/flights/{flight_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_flight():
    """Test getting a non-existent flight"""
    response = client.get("/flights/99999")
    assert response.status_code == 404


def test_create_duplicate_flight_number(sample_flight_data):
    """Test creating a flight with duplicate flight number"""
    # Create first flight
    client.post("/flights", json=sample_flight_data)
    
    # Try to create another with same flight number
    response = client.post("/flights", json=sample_flight_data)
    assert response.status_code == 409


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

