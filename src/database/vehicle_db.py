"""Vehicle Database - Manages SQLite database for authorized vehicles."""

import sqlite3
from typing import Optional, List, Tuple
from difflib import SequenceMatcher


class VehicleDB:
    """SQLite database for managing authorized vehicles."""
    
    def __init__(self, db_path: str = "authorized_vehicles.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authorized_vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                distance REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_vehicle(self, plate_number: str) -> bool:
        """Add vehicle to authorized list. Returns True if added, False if exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO authorized_vehicles (plate_number) VALUES (?)",
                (plate_number.upper().strip(),)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def remove_vehicle(self, plate_number: str) -> bool:
        """Remove vehicle from authorized list. Returns True if removed."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM authorized_vehicles WHERE plate_number = ?",
            (plate_number.upper().strip(),)
        )
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def is_authorized(self, plate_number: str) -> bool:
        """Check if vehicle is authorized."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM authorized_vehicles WHERE plate_number = ?",
            (plate_number.upper().strip(),)
        )
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def get_all_vehicles(self) -> List[dict]:
        """Get all authorized vehicles."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, plate_number, created_at FROM authorized_vehicles ORDER BY plate_number"
        )
        vehicles = [
            {'id': row[0], 'plate_number': row[1], 'created_at': row[2]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return vehicles
    
    def log_detection_event(self, event_type: str, distance: Optional[float] = None):
        """Log detection event to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO detection_events (event_type, distance) VALUES (?, ?)",
            (event_type, distance)
        )
        conn.commit()
        conn.close()
    
    def get_recent_events(self, limit: int = 50) -> List[dict]:
        """Get recent detection events."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, event_type, distance, timestamp 
            FROM detection_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        events = [
            {'id': row[0], 'event_type': row[1], 'distance': row[2], 'timestamp': row[3]}
            for row in cursor.fetchall()
        ]
        conn.close()
        return events
    
    def find_similar_plates(self, plate_number: str, threshold: float = 0.85) -> List[Tuple[str, float]]:
        """Find similar license plates using fuzzy matching."""
        plate_upper = plate_number.upper().strip()
        all_vehicles = self.get_all_vehicles()
        
        matches = []
        for vehicle in all_vehicles:
            similarity = SequenceMatcher(None, plate_upper, vehicle['plate_number']).ratio()
            if similarity >= threshold:
                matches.append((vehicle['plate_number'], similarity))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
