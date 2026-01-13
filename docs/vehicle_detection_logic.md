# Vehicle Detection Logic

## Overview
Simulates vehicle arrival detection using mocked distance sensors. Checks if vehicle is within configurable threshold and emits events.

## Detection Logic

### Pseudocode
```
INITIALIZE: sensor = MockSensor(), detector = VehicleDetector(sensor, threshold=10cm), state = NO_VEHICLE

LOOP:
    distance = sensor.get_distance()
    IF distance < threshold AND state != VEHICLE_DETECTED:
        state = VEHICLE_DETECTED
        EMIT VEHICLE_DETECTED event
    ELSE IF distance >= threshold AND state != NO_VEHICLE:
        state = NO_VEHICLE
        EMIT NO_VEHICLE event
    WAIT polling_interval
```

## Detection Conditions

- **Vehicle detected**: distance < threshold (default: 10cm)
- **Vehicle cleared**: distance >= threshold

## Events

### VEHICLE_DETECTED
Emitted when vehicle first detected within threshold.
- `distance`: Current reading (cm)
- `threshold`: Detection threshold (cm)
- `timestamp`: ISO format timestamp

### NO_VEHICLE
Emitted when vehicle moves away (distance >= threshold).
- Same data structure as VEHICLE_DETECTED

## Mock Sensor Modes

**Manual**: User sets distance values
```python
sensor = MockSensor(mode="manual")
sensor.set_distance(8.0)  # Vehicle detected
```

**Random**: Generates random readings (2-100cm)
```python
sensor = MockSensor(mode="random")
distance = sensor.get_distance()
```

**Scenario**: Predefined sequence playback
```python
sensor = MockSensor(mode="scenario")
sensor.set_scenario([{"distance": 50}, {"distance": 8}, {"distance": 25}])
```

## Usage Example

```python
from src.vehicle_detection import VehicleDetector, MockSensor

sensor = MockSensor(mode="manual")
detector = VehicleDetector(sensor, threshold_cm=10.0)

def on_detected(event):
    print(f"Vehicle detected at {event['data']['distance']}cm")

detector.on_vehicle_detected(on_detected)
sensor.set_distance(8.0)
detector.check()  # Emits VEHICLE_DETECTED
```
