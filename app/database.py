"""
Database connection and session management
"""
import sqlite3
from typing import Generator
from contextlib import contextmanager
from pathlib import Path


DATABASE_PATH = Path("flights.db")


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with flights table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT NOT NULL UNIQUE,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            aircraft_type TEXT NOT NULL,
            seats_total INTEGER NOT NULL,
            seats_available INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            process_id TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")

