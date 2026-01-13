"""Demo: Vehicle Detection - Demonstrates vehicle detection using different mock sensor modes."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vehicle_detection import VehicleDetector, MockSensor
from src.vehicle_detection.detector import VEHICLE_DETECTED, NO_VEHICLE


def print_event(event):
    """Print event information."""
    event_type = event['type']
    timestamp = event['timestamp']
    data = event['data']
    
    if event_type == VEHICLE_DETECTED:
        print(f"🚗 [{timestamp}] VEHICLE_DETECTED - Distance: {data['distance']:.1f}cm (threshold: {data['threshold']}cm)")
    else:
        print(f"   [{timestamp}] NO_VEHICLE - Distance: {data['distance']:.1f}cm")


def demo_manual_mode():
    """Demo: Manual trigger mode."""
    print("\n" + "="*60)
    print("Demo 1: Manual Trigger Mode")
    print("="*60)
    
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    detector.on_vehicle_detected(print_event)
    detector.on_no_vehicle(print_event)
    
    print("\nSimulating vehicle approach...")
    for dist in [50, 30, 15, 8, 5, 3]:
        sensor.set_distance(dist)
        detector.check()
    
    print("\nSimulating vehicle departure...")
    for dist in [5, 12, 25, 40, 60]:
        sensor.set_distance(dist)
        detector.check()


def demo_random_mode():
    """Demo: Random mode."""
    print("\n" + "="*60)
    print("Demo 2: Random Mode")
    print("="*60)
    
    sensor = MockSensor(mode="random")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    detector.on_vehicle_detected(print_event)
    detector.on_no_vehicle(print_event)
    
    print("\nRunning 10 random readings...")
    for _ in range(10):
        detector.check()


def demo_scenario_mode():
    """Demo: Scenario playback mode."""
    print("\n" + "="*60)
    print("Demo 3: Scenario Mode")
    print("="*60)
    
    sensor = MockSensor(mode="scenario")
    scenario = [
        {"distance": 50}, {"distance": 30}, {"distance": 15},
        {"distance": 8}, {"distance": 5}, {"distance": 4},
        {"distance": 12}, {"distance": 25}, {"distance": 45},
    ]
    sensor.set_scenario(scenario)
    
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    detector.on_vehicle_detected(print_event)
    detector.on_no_vehicle(print_event)
    
    print("\nPlaying scenario...")
    for _ in range(len(scenario)):
        detector.check()


def demo_interactive():
    """Demo: Interactive mode."""
    print("\n" + "="*60)
    print("Demo 4: Interactive Mode")
    print("="*60)
    print("\nEnter distance values (or 'q' to quit):")
    
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    detector.on_vehicle_detected(print_event)
    detector.on_no_vehicle(print_event)
    
    while True:
        try:
            user_input = input("\nDistance (cm): ").strip()
            if user_input.lower() == 'q':
                break
            sensor.set_distance(float(user_input))
            detector.check()
        except ValueError:
            print("Invalid input. Enter a number or 'q' to quit.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Vehicle Detection Demo - Mock Sensor")
    print("="*60)
    
    demo_manual_mode()
    demo_random_mode()
    demo_scenario_mode()
    
    print("\n" + "="*60)
    if input("Run interactive demo? (y/n): ").strip().lower() == 'y':
        demo_interactive()
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
