"""Vehicle Detection Module - Simulates vehicle detection using mocked sensors."""

from .detector import VehicleDetector
from .sensor_mock import MockSensor

__all__ = ['VehicleDetector', 'MockSensor']
