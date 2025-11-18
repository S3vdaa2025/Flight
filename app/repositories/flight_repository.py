"""
Repository layer for flight data access
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import sqlite3
from app.database import get_db
from app.models import FlightFilter, FlightSort, PaginationParams
from app.exceptions import FlightNotFoundError, FlightNumberExistsError


class FlightRepository:
    """Repository for flight database operations"""

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        return {
            'flight_id': row['flight_id'],
            'flight_number': row['flight_number'],
            'origin': row['origin'],
            'destination': row['destination'],
            'departure_time': datetime.fromisoformat(row['departure_time']),
            'arrival_time': datetime.fromisoformat(row['arrival_time']),
            'duration_minutes': row['duration_minutes'],
            'aircraft_type': row['aircraft_type'],
            'seats_total': row['seats_total'],
            'seats_available': row['seats_available'],
            'status': row['status'],
            'created_at': datetime.fromisoformat(row['created_at']),
            'updated_at': datetime.fromisoformat(row['updated_at']),
            'process_id': row['process_id']
        }

    @staticmethod
    def create(flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new flight record"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if flight number already exists
            cursor.execute("SELECT flight_id FROM flights WHERE flight_number = ?", 
                         (flight_data['flight_number'],))
            if cursor.fetchone():
                raise FlightNumberExistsError(flight_data['flight_number'])
            
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO flights (
                    flight_number, origin, destination, departure_time, arrival_time,
                    duration_minutes, aircraft_type, seats_total, seats_available,
                    status, created_at, updated_at, process_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flight_data['flight_number'],
                flight_data['origin'],
                flight_data['destination'],
                flight_data['departure_time'].isoformat(),
                flight_data['arrival_time'].isoformat(),
                flight_data['duration_minutes'],
                flight_data['aircraft_type'],
                flight_data['seats_total'],
                flight_data['seats_available'],
                flight_data['status'],
                now,
                now,
                flight_data['process_id']
            ))
            
            flight_id = cursor.lastrowid
            conn.commit()
            
            return FlightRepository.get_by_id(flight_id)

    @staticmethod
    def get_by_id(flight_id: int) -> Dict[str, Any]:
        """Get a flight by ID"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
            row = cursor.fetchone()
            
            if not row:
                raise FlightNotFoundError(flight_id)
            
            return FlightRepository._row_to_dict(row)

    @staticmethod
    def get_all(
        filters: Optional[FlightFilter] = None,
        sort: Optional[FlightSort] = None,
        pagination: Optional[PaginationParams] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all flights with optional filtering, sorting, and pagination"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause
            where_clauses = []
            params = []
            
            if filters:
                if filters.origin:
                    where_clauses.append("origin = ?")
                    params.append(filters.origin)
                if filters.destination:
                    where_clauses.append("destination = ?")
                    params.append(filters.destination)
                if filters.status:
                    where_clauses.append("status = ?")
                    params.append(filters.status)
                if filters.aircraft_type:
                    where_clauses.append("aircraft_type = ?")
                    params.append(filters.aircraft_type)
                if filters.min_seats_available is not None:
                    where_clauses.append("seats_available >= ?")
                    params.append(filters.min_seats_available)
                if filters.max_seats_available is not None:
                    where_clauses.append("seats_available <= ?")
                    params.append(filters.max_seats_available)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Build ORDER BY clause
            valid_sort_fields = [
                'flight_id', 'flight_number', 'origin', 'destination',
                'departure_time', 'arrival_time', 'duration_minutes',
                'aircraft_type', 'seats_total', 'seats_available', 'status',
                'created_at', 'updated_at', 'process_id'
            ]
            
            sort_field = sort.field if sort and sort.field in valid_sort_fields else 'flight_id'
            sort_order = sort.order.upper() if sort and sort.order.lower() == 'desc' else 'ASC'
            
            # Get total count
            count_sql = f"SELECT COUNT(*) FROM flights WHERE {where_sql}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # Build pagination
            if pagination:
                offset = (pagination.page - 1) * pagination.page_size
                limit = pagination.page_size
            else:
                offset = 0
                limit = 100  # Default limit
            
            # Get paginated results
            sql = f"""
                SELECT * FROM flights 
                WHERE {where_sql}
                ORDER BY {sort_field} {sort_order}
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, params + [limit, offset])
            rows = cursor.fetchall()
            
            flights = [FlightRepository._row_to_dict(row) for row in rows]
            return flights, total

    @staticmethod
    def update(flight_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a flight record"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if flight exists
            cursor.execute("SELECT flight_id FROM flights WHERE flight_id = ?", (flight_id,))
            if not cursor.fetchone():
                raise FlightNotFoundError(flight_id)
            
            # Check if flight number is being updated and already exists
            if 'flight_number' in update_data:
                cursor.execute(
                    "SELECT flight_id FROM flights WHERE flight_number = ? AND flight_id != ?",
                    (update_data['flight_number'], flight_id)
                )
                if cursor.fetchone():
                    raise FlightNumberExistsError(update_data['flight_number'])
            
            # Build UPDATE clause
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                if value is not None:
                    if isinstance(value, datetime):
                        set_clauses.append(f"{key} = ?")
                        params.append(value.isoformat())
                    else:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)
            
            if not set_clauses:
                return FlightRepository.get_by_id(flight_id)
            
            set_clauses.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(flight_id)
            
            sql = f"UPDATE flights SET {', '.join(set_clauses)} WHERE flight_id = ?"
            cursor.execute(sql, params)
            conn.commit()
            
            return FlightRepository.get_by_id(flight_id)

    @staticmethod
    def delete(flight_id: int) -> bool:
        """Delete a flight record"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if flight exists
            cursor.execute("SELECT flight_id FROM flights WHERE flight_id = ?", (flight_id,))
            if not cursor.fetchone():
                raise FlightNotFoundError(flight_id)
            
            cursor.execute("DELETE FROM flights WHERE flight_id = ?", (flight_id,))
            conn.commit()
            
            return True

