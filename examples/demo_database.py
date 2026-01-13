"""Demo: Vehicle Database - Demonstrates SQLite database operations."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import VehicleDB


def demo_database_operations():
    """Demonstrate database operations."""
    print("\n" + "="*60)
    print("Vehicle Database Demo")
    print("="*60)
    
    db = VehicleDB("demo_vehicles.db")
    print("\n✅ Database initialized")
    
    print("\n--- Adding Vehicles ---")
    for plate in ["ABC123", "XYZ789", "DEF456"]:
        status = "✅ Added" if db.add_vehicle(plate) else "⚠️  Already exists"
        print(f"{status}: {plate}")
    
    print("\n--- Adding Duplicate ---")
    print("⚠️  Already exists (expected)" if not db.add_vehicle("ABC123") else "✅ Added")
    
    print("\n--- Checking Authorization ---")
    for plate in ["ABC123", "XYZ789", "UNKNOWN"]:
        status = "✅ authorized" if db.is_authorized(plate) else "❌ NOT authorized"
        print(f"{status}: {plate}")
    
    print("\n--- All Authorized Vehicles ---")
    for v in db.get_all_vehicles():
        print(f"  {v['plate_number']} (ID: {v['id']}, Added: {v['created_at']})")
    
    print("\n--- Logging Detection Events ---")
    for event_type, distance in [("VEHICLE_DETECTED", 8.5), ("NO_VEHICLE", 25.0), ("VEHICLE_DETECTED", 7.2)]:
        db.log_detection_event(event_type, distance)
    print("✅ Logged 3 events")
    
    print("\n--- Recent Detection Events ---")
    for event in db.get_recent_events(limit=10):
        dist_str = f"{event['distance']}cm" if event['distance'] else "N/A"
        print(f"  {event['event_type']} - Distance: {dist_str} - {event['timestamp']}")
    
    print("\n--- Removing Vehicle ---")
    print("✅ Removed: DEF456" if db.remove_vehicle("DEF456") else "❌ Not found: DEF456")
    
    print("\n--- Verifying Removal ---")
    print("✅ Correctly removed" if not db.is_authorized("DEF456") else "⚠️  Still authorized")
    
    print("\n--- Cleanup ---")
    if os.path.exists("demo_vehicles.db"):
        os.remove("demo_vehicles.db")
        print("✅ Demo database removed")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_database_operations()
