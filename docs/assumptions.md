# Assumptions and Constraints

## Assumptions

1. **Distance Units**: All measurements in centimeters (cm)
2. **Sensor Readings**: Valid range 2-100cm. Below threshold = vehicle present
3. **Detection Logic**: Vehicle detected when distance < threshold (default: 10cm). Single vehicle at a time
4. **Mock Sensor**: Uses mocked readings, will be replaced with real hardware (ultrasonic sensor)
5. **Event Emission**: Synchronous events with timestamp and distance data
6. **Configuration**: Threshold configurable via YAML, default 10cm, runtime updates supported

## Constraints

1. **No Hardware Dependency**: Pure software simulation, testable without hardware
2. **Python Version**: Requires Python 3.11+, compatible with Raspberry Pi OS
3. **Single Detection Point**: One detection zone, one sensor reading at a time
4. **Polling-Based**: Uses polling (not interrupt-driven), configurable interval
5. **No Debouncing**: State changes immediately on threshold crossing (can be added later)

## Future Considerations

- **Hardware Integration**: Replace mock with real ultrasonic sensor, use RPi.GPIO/lgpio
- **Enhanced Features**: Debouncing, multiple sensors, direction detection, confidence scoring
- **Performance**: Async event handling, optimized polling, event queuing
