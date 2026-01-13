# Vehicle Detection Module

Simple vehicle detection using mocked distance sensors.

## Quick Start

```python
from src.vehicle_detection import VehicleDetector, MockSensor

# Create sensor and detector
sensor = MockSensor(mode="manual")
detector = VehicleDetector(sensor, threshold_cm=10.0)

# Handle events
def on_detected(event):
    print("Vehicle detected!")

detector.on_vehicle_detected(on_detected)

# Check for vehicle
sensor.set_distance(8.0)
detector.check()
```

## Run Demo

```bash
python examples/demo_detection.py
```

## Files

- `sensor_mock.py` - Mock sensor generator
- `detector.py` - Detection logic and event emission

## Events

- `VEHICLE_DETECTED` - Emitted when distance < threshold
- `NO_VEHICLE` - Emitted when distance >= threshold
