"""Integration tests: detector + database with mock sensor."""

import pytest

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED, NO_VEHICLE
from src.database import VehicleDB


def test_detector_events_logged_to_db(temp_db_path):
    """Detection events are logged to database when detector runs."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB(temp_db_path)
    db.add_vehicle("TEST1")

    def log_event(event):
        db.log_detection_event(event["type"], event["data"].get("distance"))

    detector.on_vehicle_detected(log_event)
    detector.on_no_vehicle(log_event)

    sensor.set_distance(8.0)
    detector.check()
    sensor.set_distance(25.0)
    detector.check()
    sensor.set_distance(5.0)
    detector.check()

    events = db.get_recent_events(limit=10)
    assert len(events) == 3
    types = [e["event_type"] for e in events]
    assert VEHICLE_DETECTED in types
    assert NO_VEHICLE in types
    distances = [e["distance"] for e in events if e["distance"] is not None]
    assert 8.0 in distances
    assert 25.0 in distances
    assert 5.0 in distances


def test_scenario_sequence_produces_expected_events(temp_db_path):
    """Running a predefined scenario produces expected detection events in DB."""
    sensor = MockSensor(mode="manual")
    sensor.set_mode("scenario")
    scenario = sensor.get_predefined_scenario("quick_pass")
    assert scenario is not None
    sensor.set_scenario(scenario)

    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB(temp_db_path)
    logged = []

    def log_event(event):
        db.log_detection_event(event["type"], event["data"].get("distance"))
        logged.append(event["type"])

    detector.on_vehicle_detected(log_event)
    detector.on_no_vehicle(log_event)

    for _ in scenario:
        detector.check()

    events_in_db = db.get_recent_events(limit=20)
    assert len(events_in_db) >= 1
    assert any(e["event_type"] == VEHICLE_DETECTED for e in events_in_db)
