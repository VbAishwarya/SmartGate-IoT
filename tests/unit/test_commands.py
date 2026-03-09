"""Unit tests for command handler (with mocked sensor, detector, db)."""

import pytest

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED
from src.database import VehicleDB
from src.common.commands import CommandHandler


class TestCommandHandler:
    """CommandHandler with mock dependencies."""

    def test_handle_status(self, mock_sensor, detector, vehicle_db, capsys):
        handler = CommandHandler(mock_sensor, detector, vehicle_db)
        mock_sensor.set_distance(8.0)
        detector.check()
        handler.handle_status()
        out = capsys.readouterr().out
        assert "State" in out
        assert VEHICLE_DETECTED in out or "10" in out

    def test_handle_vehicles(self, vehicle_db, capsys):
        handler = CommandHandler(
            MockSensor(mode="manual"),
            VehicleDetector(MockSensor(mode="manual"), threshold_cm=10.0),
            vehicle_db,
        )
        handler.handle_vehicles()
        out = capsys.readouterr().out
        assert "ABC123" in out or "Authorized" in out

    def test_handle_check_authorized(self, vehicle_db, capsys):
        handler = CommandHandler(
            MockSensor(mode="manual"),
            VehicleDetector(MockSensor(mode="manual"), threshold_cm=10.0),
            vehicle_db,
        )
        handler.handle_check("ABC123")
        out = capsys.readouterr().out
        assert "authorized" in out.lower()

    def test_handle_check_unauthorized(self, vehicle_db, capsys):
        handler = CommandHandler(
            MockSensor(mode="manual"),
            VehicleDetector(MockSensor(mode="manual"), threshold_cm=10.0),
            vehicle_db,
        )
        handler.handle_check("UNKNOWN99")
        out = capsys.readouterr().out
        assert "not authorized" in out.lower() or "denied" in out.lower() or "similar" in out.lower()

    def test_handle_distance(self, mock_sensor, detector, vehicle_db):
        handler = CommandHandler(mock_sensor, detector, vehicle_db)
        handler.handle_distance("7.5")
        assert mock_sensor.get_distance() == 7.5
        assert detector.current_state == VEHICLE_DETECTED

    def test_handle_events(self, vehicle_db, capsys):
        vehicle_db.log_detection_event("VEHICLE_DETECTED", distance=9.0)
        handler = CommandHandler(
            MockSensor(mode="manual"),
            VehicleDetector(MockSensor(mode="manual"), threshold_cm=10.0),
            vehicle_db,
        )
        handler.handle_events()
        out = capsys.readouterr().out
        assert "VEHICLE_DETECTED" in out or "Event" in out
