"""Unit tests for vehicle detection module (detector + mock sensor)."""

import pytest

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED, NO_VEHICLE


class TestVehicleDetector:
    """Vehicle detection with mock sensor."""

    def test_vehicle_detected_when_below_threshold(self, mock_sensor, detector):
        events = []
        detector.on_vehicle_detected(events.append)
        detector.on_no_vehicle(events.append)
        mock_sensor.set_distance(8.0)
        detector.check()
        assert len(events) == 1
        assert events[0]["type"] == VEHICLE_DETECTED
        assert events[0]["data"]["distance"] == 8.0

    def test_no_vehicle_when_above_threshold(self, mock_sensor, detector):
        events = []
        detector.on_vehicle_detected(events.append)
        detector.on_no_vehicle(events.append)
        mock_sensor.set_distance(8.0)
        detector.check()
        mock_sensor.set_distance(15.0)
        detector.check()
        assert len(events) == 2
        assert events[0]["type"] == VEHICLE_DETECTED
        assert events[1]["type"] == NO_VEHICLE
        assert events[1]["data"]["distance"] == 15.0

    def test_state_transitions(self, mock_sensor, detector):
        events = []
        detector.on_vehicle_detected(events.append)
        detector.on_no_vehicle(events.append)
        mock_sensor.set_distance(8.0)
        detector.check()
        assert len(events) == 1 and events[0]["type"] == VEHICLE_DETECTED
        mock_sensor.set_distance(20.0)
        detector.check()
        assert len(events) == 2 and events[1]["type"] == NO_VEHICLE
        mock_sensor.set_distance(8.0)
        detector.check()
        assert len(events) == 3 and events[2]["type"] == VEHICLE_DETECTED

    def test_threshold_configuration(self, mock_sensor, detector):
        events = []
        detector.on_vehicle_detected(events.append)
        mock_sensor.set_distance(8.0)
        detector.check()
        assert len(events) == 1
        detector.set_threshold(5.0)
        events.clear()
        mock_sensor.set_distance(8.0)
        detector.check()
        assert len(events) == 0
        mock_sensor.set_distance(4.0)
        detector.check()
        assert len(events) == 1 and events[0]["type"] == VEHICLE_DETECTED

    def test_exact_threshold_boundary(self, mock_sensor):
        detector = VehicleDetector(mock_sensor, threshold_cm=10.0)
        events = []
        detector.on_vehicle_detected(events.append)
        detector.on_no_vehicle(events.append)
        mock_sensor.set_distance(5.0)
        detector.check()
        assert detector.current_state == VEHICLE_DETECTED
        events.clear()
        mock_sensor.set_distance(10.0)
        result = detector.check()
        assert result == NO_VEHICLE
        assert len(events) == 1 and events[0]["type"] == NO_VEHICLE

    def test_no_events_without_listeners(self, mock_sensor, detector):
        mock_sensor.set_distance(5.0)
        detector.check()
        assert detector.current_state == VEHICLE_DETECTED

    def test_event_contains_timestamp_and_data(self, mock_sensor, detector):
        events = []
        detector.on_vehicle_detected(events.append)
        mock_sensor.set_distance(7.0)
        detector.check()
        assert "timestamp" in events[0]
        assert events[0]["data"]["distance"] == 7.0
        assert events[0]["data"]["threshold"] == 10.0


class TestMockSensor:
    """Mock sensor behavior."""

    def test_manual_mode_returns_set_distance(self, mock_sensor):
        mock_sensor.set_distance(42.0)
        assert mock_sensor.get_distance() == 42.0

    def test_scenario_mode_returns_sequence(self, mock_sensor):
        mock_sensor.set_mode("scenario")
        mock_sensor.set_scenario([
            {"distance": 50, "delay": 0.1},
            {"distance": 8, "delay": 0.1},
        ])
        assert mock_sensor.get_distance() == 50.0
        assert mock_sensor.get_distance() == 8.0
        assert mock_sensor.get_distance() == 8.0  # last repeats

    def test_predefined_scenario_exists(self, mock_sensor):
        scenario = mock_sensor.get_predefined_scenario("quick_pass")
        assert scenario is not None
        assert len(scenario) >= 1
        assert "distance" in scenario[0]

    def test_predefined_scenario_unknown_returns_none(self, mock_sensor):
        assert mock_sensor.get_predefined_scenario("nonexistent") is None
