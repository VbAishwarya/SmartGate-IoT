"""Tests for vehicle database."""

import sys
import os
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import VehicleDB


def test_add_vehicle():
    """Test adding vehicles to database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = VehicleDB(db_path)
        assert db.add_vehicle("TEST123") == True
        assert db.add_vehicle("TEST123") == False
        assert db.is_authorized("TEST123") == True
        assert db.is_authorized("UNKNOWN") == False
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_remove_vehicle():
    """Test removing vehicles from database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = VehicleDB(db_path)
        db.add_vehicle("TEST456")
        assert db.is_authorized("TEST456") == True
        
        assert db.remove_vehicle("TEST456") == True
        assert db.is_authorized("TEST456") == False
        assert db.remove_vehicle("TEST456") == False
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_get_all_vehicles():
    """Test getting all vehicles."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = VehicleDB(db_path)
        for plate in ["VEH1", "VEH2", "VEH3"]:
            db.add_vehicle(plate)
        
        vehicles = db.get_all_vehicles()
        assert len(vehicles) == 3
        
        plate_numbers = [v['plate_number'] for v in vehicles]
        assert all(plate in plate_numbers for plate in ["VEH1", "VEH2", "VEH3"])
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_log_events():
    """Test logging detection events."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = VehicleDB(db_path)
        db.log_detection_event("VEHICLE_DETECTED", distance=8.5)
        time.sleep(0.01)
        db.log_detection_event("NO_VEHICLE", distance=25.0)
        
        events = db.get_recent_events(limit=10)
        assert len(events) == 2
        
        event_types = [e['event_type'] for e in events]
        assert "VEHICLE_DETECTED" in event_types
        assert "NO_VEHICLE" in event_types
        
        distances = {e['event_type']: e['distance'] for e in events}
        assert distances.get("VEHICLE_DETECTED") == 8.5
        assert distances.get("NO_VEHICLE") == 25.0
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    print("Running database tests...")
    test_add_vehicle()
    print("✓ test_add_vehicle passed")
    
    test_remove_vehicle()
    print("✓ test_remove_vehicle passed")
    
    test_get_all_vehicles()
    print("✓ test_get_all_vehicles passed")
    
    test_log_events()
    print("✓ test_log_events passed")
    
    print("\nAll tests passed! ✅")
