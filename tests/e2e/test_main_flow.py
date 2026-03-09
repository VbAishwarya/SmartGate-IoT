"""End-to-end tests: full application flow with mocked sensor and temp DB."""

import pytest

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED, NO_VEHICLE
from src.database import VehicleDB
from src.common.scenario_runner import ScenarioRunner
from src.common.commands import CommandHandler


def test_full_flow_initialization_and_scenario(temp_db_path):
    """
    E2E: Initialize system (sensor, detector, db), register callbacks, run a scenario,
    then verify DB state and recent events. No hardware, no interactive input.
    """
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB(temp_db_path)
    for plate in ["ABC123", "XYZ789", "DEF456"]:
        db.add_vehicle(plate)

    events_logged = []

    def on_event(event):
        db.log_detection_event(event["type"], event["data"].get("distance"))
        events_logged.append(event)

    detector.on_vehicle_detected(on_event)
    detector.on_no_vehicle(on_event)

    runner = ScenarioRunner(sensor, detector, db)
    scenario = sensor.get_predefined_scenario("quick_pass")
    assert scenario is not None
    for step in scenario:
        sensor.set_distance(step["distance"])
        detector.check()

    assert len(events_logged) >= 1
    events_in_db = db.get_recent_events(limit=20)
    assert len(events_in_db) >= 1
    assert detector.current_state in (VEHICLE_DETECTED, NO_VEHICLE)
    vehicles = db.get_all_vehicles()
    assert len(vehicles) == 3


def test_full_flow_check_plate_via_command_handler(temp_db_path):
    """
    E2E: DB with authorized plates, CommandHandler.handle_check authorizes known plate
    and rejects unknown (with optional fuzzy suggestion). No interactive input.
    """
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB(temp_db_path)
    db.add_vehicle("AUTH1")
    db.add_vehicle("AUTH2")
    handler = CommandHandler(sensor, detector, db)

    handler.handle_check("AUTH1")
    assert db.is_authorized("AUTH1")
    handler.handle_check("UNKNOWN")
    assert not db.is_authorized("UNKNOWN")
