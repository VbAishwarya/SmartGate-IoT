"""Vehicle Detector - Detects vehicles based on distance threshold and emits events."""

import time
from typing import Callable, Optional
from datetime import datetime
from .sensor_mock import MockSensor

VEHICLE_DETECTED = "VEHICLE_DETECTED"
NO_VEHICLE = "NO_VEHICLE"


class VehicleDetector:
    """Detects vehicles using distance threshold logic."""
    
    def __init__(self, sensor: MockSensor, threshold_cm: float = 10.0):
        self.sensor = sensor
        self.threshold_cm = threshold_cm
        self.current_state = NO_VEHICLE
        self.event_listeners = {
            VEHICLE_DETECTED: [],
            NO_VEHICLE: []
        }
    
    def set_threshold(self, threshold_cm: float):
        """Update detection threshold."""
        self.threshold_cm = threshold_cm
    
    def on_vehicle_detected(self, callback: Callable):
        """Register callback for VEHICLE_DETECTED event."""
        self.event_listeners[VEHICLE_DETECTED].append(callback)
    
    def on_no_vehicle(self, callback: Callable):
        """Register callback for NO_VEHICLE event."""
        self.event_listeners[NO_VEHICLE].append(callback)
    
    def _emit_event(self, event_type: str, data: dict):
        """Emit event to all registered listeners."""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        for callback in self.event_listeners[event_type]:
            callback(event)
    
    def check(self) -> Optional[str]:
        """Check current sensor reading and emit events if state changed."""
        distance = self.sensor.get_distance()
        
        if distance < self.threshold_cm:
            if self.current_state != VEHICLE_DETECTED:
                self.current_state = VEHICLE_DETECTED
                self._emit_event(VEHICLE_DETECTED, {
                    'distance': distance,
                    'threshold': self.threshold_cm
                })
                return VEHICLE_DETECTED
        else:
            if self.current_state != NO_VEHICLE:
                self.current_state = NO_VEHICLE
                self._emit_event(NO_VEHICLE, {
                    'distance': distance,
                    'threshold': self.threshold_cm
                })
                return NO_VEHICLE
        
        return None
    
    def run_continuous(self, interval_seconds: float = 0.5, max_iterations: Optional[int] = None):
        """Run continuous detection loop."""
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            self.check()
            time.sleep(interval_seconds)
            iteration += 1
