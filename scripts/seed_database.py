"""
Script to seed database with sample flight data from JSON file
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, get_db
from app.repositories.flight_repository import FlightRepository
from datetime import datetime


def load_sample_data(json_path: str = "data/flights_sample.json"):
    """Load sample data from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def seed_database():
    """Seed database with sample flight data"""
    # Initialize database
    init_db()
    
    # Load sample data
    sample_data = load_sample_data()
    
    # Insert flights
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flights")  # Clear existing data
        conn.commit()
    
    inserted_count = 0
    skipped_count = 0
    
    for flight_data in sample_data:
        try:
            # Convert datetime strings to datetime objects
            flight_data['departure_time'] = datetime.fromisoformat(flight_data['departure_time'])
            flight_data['arrival_time'] = datetime.fromisoformat(flight_data['arrival_time'])
            flight_data['created_at'] = datetime.fromisoformat(flight_data['created_at'])
            flight_data['updated_at'] = datetime.fromisoformat(flight_data['updated_at'])
            
            # Remove flight_id as it will be auto-generated
            flight_id = flight_data.pop('flight_id', None)
            
            FlightRepository.create(flight_data)
            inserted_count += 1
            print(f"✓ Inserted flight: {flight_data['flight_number']}")
        except Exception as e:
            skipped_count += 1
            print(f"✗ Skipped flight {flight_data.get('flight_number', 'unknown')}: {str(e)}")
    
    print(f"\n✓ Database seeded successfully!")
    print(f"  Inserted: {inserted_count} flights")
    print(f"  Skipped: {skipped_count} flights")


if __name__ == "__main__":
    seed_database()

