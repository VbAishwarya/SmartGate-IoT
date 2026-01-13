"""Tests for vehicle detector."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED, NO_VEHICLE


def test_vehicle_detection():
    """Test vehicle detection when distance < threshold."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    
    events = []
    def capture_event(event):
        events.append(event)
    
    detector.on_vehicle_detected(capture_event)
    detector.on_no_vehicle(capture_event)
    
    sensor.set_distance(8.0)
    detector.check()
    
    assert len(events) == 1
    assert events[0]['type'] == VEHICLE_DETECTED
    assert events[0]['data']['distance'] == 8.0


def test_no_vehicle():
    """Test NO_VEHICLE emission when distance >= threshold."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    
    events = []
    def capture_event(event):
        events.append(event)
    
    detector.on_vehicle_detected(capture_event)
    detector.on_no_vehicle(capture_event)
    
    sensor.set_distance(8.0)
    detector.check()
    sensor.set_distance(15.0)
    detector.check()
    
    assert len(events) == 2
    assert events[0]['type'] == VEHICLE_DETECTED
    assert events[1]['type'] == NO_VEHICLE
    assert events[1]['data']['distance'] == 15.0


def test_state_transition():
    """Test state transitions."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    
    events = []
    def capture_event(event):
        events.append(event)
    
    detector.on_vehicle_detected(capture_event)
    detector.on_no_vehicle(capture_event)
    
    sensor.set_distance(8.0)
    detector.check()
    assert len(events) == 1
    assert events[0]['type'] == VEHICLE_DETECTED
    
    sensor.set_distance(20.0)
    detector.check()
    assert len(events) == 2
    assert events[1]['type'] == NO_VEHICLE
    
    sensor.set_distance(8.0)
    detector.check()
    assert len(events) == 3
    assert events[2]['type'] == VEHICLE_DETECTED


def test_threshold_configuration():
    """Test threshold configuration."""
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    
    events = []
    def capture_event(event):
        events.append(event)
    
    detector.on_vehicle_detected(capture_event)
    
    sensor.set_distance(8.0)
    detector.check()
    assert len(events) == 1
    
    detector.set_threshold(5.0)
    events.clear()
    
    sensor.set_distance(8.0)
    detector.check()
    assert len(events) == 0
    
    sensor.set_distance(4.0)
    detector.check()
    assert len(events) == 1
    assert events[0]['type'] == VEHICLE_DETECTED


if __name__ == "__main__":
    print("Running tests...")
    test_vehicle_detection()
    print("✓ test_vehicle_detection passed")
    
    test_no_vehicle()
    print("✓ test_no_vehicle passed")
    
    test_state_transition()
    print("✓ test_state_transition passed")
    
    test_threshold_configuration()
    print("✓ test_threshold_configuration passed")
    
    print("\nAll tests passed! ✅")
