"""Unit tests for vehicle database module."""

import pytest

from src.database import VehicleDB


class TestVehicleDB:
    """VehicleDB with temporary database."""

    def test_add_vehicle(self, temp_db_path):
        db = VehicleDB(temp_db_path)
        assert db.add_vehicle("TEST123") is True
        assert db.add_vehicle("TEST123") is False
        assert db.is_authorized("TEST123") is True
        assert db.is_authorized("UNKNOWN") is False

    def test_remove_vehicle(self, temp_db_path):
        db = VehicleDB(temp_db_path)
        db.add_vehicle("TEST456")
        assert db.is_authorized("TEST456") is True
        assert db.remove_vehicle("TEST456") is True
        assert db.is_authorized("TEST456") is False
        assert db.remove_vehicle("TEST456") is False

    def test_get_all_vehicles(self, empty_vehicle_db):
        db = empty_vehicle_db
        for plate in ["VEH1", "VEH2", "VEH3"]:
            db.add_vehicle(plate)
        vehicles = db.get_all_vehicles()
        assert len(vehicles) == 3
        plates = [v["plate_number"] for v in vehicles]
        assert all(p in plates for p in ["VEH1", "VEH2", "VEH3"])

    def test_log_detection_events(self, empty_vehicle_db):
        db = empty_vehicle_db
        db.log_detection_event("VEHICLE_DETECTED", distance=8.5)
        db.log_detection_event("NO_VEHICLE", distance=25.0)
        events = db.get_recent_events(limit=10)
        assert len(events) == 2
        types = {e["event_type"] for e in events}
        assert "VEHICLE_DETECTED" in types and "NO_VEHICLE" in types
        by_type = {e["event_type"]: e["distance"] for e in events}
        assert by_type.get("VEHICLE_DETECTED") == 8.5
        assert by_type.get("NO_VEHICLE") == 25.0

    def test_plate_normalized_to_upper(self, temp_db_path):
        db = VehicleDB(temp_db_path)
        db.add_vehicle("abc123")
        assert db.is_authorized("ABC123") is True
        assert db.is_authorized("  abc123  ") is True

    def test_find_similar_plates_exact(self, vehicle_db):
        matches = vehicle_db.find_similar_plates("ABC123", threshold=0.85)
        assert len(matches) >= 1
        assert matches[0][0] == "ABC123"
        assert matches[0][1] == 1.0

    def test_find_similar_plates_fuzzy(self, vehicle_db):
        # Use a typo that yields >= 0.85 similarity (e.g. one character off)
        matches = vehicle_db.find_similar_plates("ABC12", threshold=0.80)
        assert len(matches) >= 1
        assert matches[0][0] == "ABC123"
        assert matches[0][1] >= 0.80

    def test_find_similar_plates_no_match(self, vehicle_db):
        matches = vehicle_db.find_similar_plates("ZZZ999", threshold=0.85)
        assert len(matches) == 0

    def test_find_similar_plates_respects_threshold(self, vehicle_db):
        high = vehicle_db.find_similar_plates("ABC123", threshold=0.99)
        low = vehicle_db.find_similar_plates("ABC123", threshold=0.5)
        assert len(high) <= len(low)
