"""Demo: Vehicle Detection + Database Integration - Shows integrated system with logging."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.vehicle_detection import VehicleDetector, MockSensor
from src.database import VehicleDB


def demo_integrated_system():
    """Demonstrate integrated vehicle detection with database logging."""
    print("\n" + "="*60)
    print("Integrated Vehicle Detection + Database Demo")
    print("="*60)
    
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB("demo_integrated.db")
    
    print("\n--- Setting up authorized vehicles ---")
    for plate in ["ABC123", "XYZ789"]:
        db.add_vehicle(plate)
    print("✅ Added 2 authorized vehicles")
    
    def log_to_database(event):
        event_type = event['type']
        distance = event['data'].get('distance')
        db.log_detection_event(event_type, distance)
        
        if event_type == "VEHICLE_DETECTED":
            print(f"🚗 Vehicle detected at {distance:.1f}cm - Logged to database")
        else:
            print(f"   No vehicle - Distance: {distance:.1f}cm - Logged to database")
    
    detector.on_vehicle_detected(log_to_database)
    detector.on_no_vehicle(log_to_database)
    
    print("\n--- Simulating vehicle detection ---")
    for dist in [50, 30, 15, 8, 5, 12, 25, 40]:
        sensor.set_distance(dist)
        detector.check()
    
    print("\n--- Recent Detection Events from Database ---")
    for event in db.get_recent_events(limit=10):
        dist_str = f"{event['distance']:.1f}cm" if event['distance'] else "N/A"
        print(f"  {event['event_type']:20s} - {dist_str:8s} - {event['timestamp']}")
    
    print("\n--- Cleanup ---")
    if os.path.exists("demo_integrated.db"):
        os.remove("demo_integrated.db")
        print("✅ Demo database removed")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_integrated_system()
