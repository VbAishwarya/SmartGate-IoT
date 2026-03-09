"""Unit tests for scenario runner (with mocked sensor, detector, db)."""

import pytest

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED
from src.database import VehicleDB
from src.common.scenario_runner import ScenarioRunner


class TestScenarioRunner:
    """ScenarioRunner with mock dependencies."""

    def test_get_available_scenarios(self, mock_sensor, detector, vehicle_db):
        runner = ScenarioRunner(mock_sensor, detector, vehicle_db)
        scenarios = runner.get_available_scenarios()
        assert "1" in scenarios and "6" in scenarios
        assert scenarios["6"][0] == "full_flow_authorized"

    def test_run_scenario_quick_pass(self, mock_sensor, detector, vehicle_db):
        runner = ScenarioRunner(mock_sensor, detector, vehicle_db)
        scenario = mock_sensor.get_predefined_scenario("quick_pass")
        assert scenario is not None
        mock_sensor.set_mode("scenario")
        mock_sensor.set_scenario(scenario)
        events = []
        detector.on_vehicle_detected(events.append)
        detector.on_no_vehicle(events.append)
        for step in scenario:
            mock_sensor.set_distance(step["distance"])
            detector.check()
        assert len(events) >= 1
        types = [e["type"] for e in events]
        assert VEHICLE_DETECTED in types

    def test_run_scenario_full_flow_authorized(self, mock_sensor, detector, vehicle_db):
        runner = ScenarioRunner(mock_sensor, detector, vehicle_db)
        scenario = mock_sensor.get_predefined_scenario("full_flow_authorized")
        assert scenario is not None
        for step in scenario:
            mock_sensor.set_distance(step["distance"])
            event = detector.check()
            plate = step.get("plate")
            if plate and vehicle_db.is_authorized(plate):
                if event == VEHICLE_DETECTED and step["distance"] < detector.threshold_cm:
                    assert vehicle_db.is_authorized(plate)

    def test_custom_full_flow_scenario(self, mock_sensor, detector, vehicle_db):
        runner = ScenarioRunner(mock_sensor, detector, vehicle_db)
        custom = runner._create_custom_full_flow_scenario("CUSTOM99")
        assert len(custom) >= 5
        assert all("distance" in s and "plate" in s for s in custom)
        assert custom[0]["plate"] == "CUSTOM99"
