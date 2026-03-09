"""Integration tests: scenario runner flow with real detector and DB."""

import pytest

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED
from src.database import VehicleDB
from src.common.scenario_runner import ScenarioRunner


def test_run_scenario_full_flow_authorized_logs_events(temp_db_path):
    """Running full_flow_authorized scenario logs AUTHORIZED-style flow to DB."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB(temp_db_path)
    for p in ["ABC123", "XYZ789"]:
        db.add_vehicle(p)
    runner = ScenarioRunner(sensor, detector, db)

    scenario = sensor.get_predefined_scenario("full_flow_authorized")
    assert scenario is not None

    def log_event(event):
        db.log_detection_event(event["type"], event["data"].get("distance"))

    detector.on_vehicle_detected(log_event)
    detector.on_no_vehicle(log_event)

    for step in scenario:
        sensor.set_distance(step["distance"])
        detector.check()

    events = db.get_recent_events(limit=20)
    assert len(events) >= 1
    assert any(e["event_type"] == VEHICLE_DETECTED for e in events)


def test_run_scenario_full_flow_denied_no_authorization(temp_db_path):
    """Running full_flow_denied: vehicle detected but plate not in DB."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB(temp_db_path)
    db.add_vehicle("ONLYONE")
    runner = ScenarioRunner(sensor, detector, db)

    scenario = sensor.get_predefined_scenario("full_flow_denied")
    assert scenario is not None
    for step in scenario:
        sensor.set_distance(step["distance"])
        event = detector.check()
        plate = step.get("plate", "")
        if event == VEHICLE_DETECTED and plate:
            assert not db.is_authorized(plate)
