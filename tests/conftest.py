"""Shared pytest fixtures and configuration for SmartGate-IoT tests."""

import os
import sys
import tempfile

import pytest

# Ensure project root and src are on path when running tests
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


@pytest.fixture
def temp_db_path():
    """Yield a temporary database file path; file is removed after test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_sensor():
    """Yield a MockSensor in manual mode for controllable tests."""
    from src.vehicle_detection import MockSensor
    return MockSensor(mode="manual")


@pytest.fixture
def detector(mock_sensor):
    """Yield a VehicleDetector with mock sensor and 10cm threshold."""
    from src.vehicle_detection import VehicleDetector
    return VehicleDetector(mock_sensor, threshold_cm=10.0)


@pytest.fixture
def vehicle_db(temp_db_path):
    """Yield a VehicleDB instance using a temporary database."""
    from src.database import VehicleDB
    db = VehicleDB(temp_db_path)
    for plate in ["ABC123", "XYZ789", "DEF456"]:
        db.add_vehicle(plate)
    return db


@pytest.fixture
def empty_vehicle_db(temp_db_path):
    """Yield an empty VehicleDB instance."""
    from src.database import VehicleDB
    return VehicleDB(temp_db_path)
