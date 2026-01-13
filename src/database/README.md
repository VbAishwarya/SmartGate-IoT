# Database Module

SQLite database for managing authorized vehicles and logging detection events.

## Quick Start

```python
from src.database import VehicleDB

# Initialize database
db = VehicleDB("authorized_vehicles.db")

# Add authorized vehicle
db.add_vehicle("ABC123")

# Check if vehicle is authorized
if db.is_authorized("ABC123"):
    print("Vehicle is authorized")

# Log detection event
db.log_detection_event("VEHICLE_DETECTED", distance=8.5)

# Get all authorized vehicles
vehicles = db.get_all_vehicles()
```

## Run Demo

```bash
python examples/demo_database.py
```

## Database Schema

### authorized_vehicles
- `id` - Primary key
- `plate_number` - License plate (unique)
- `created_at` - Timestamp

### detection_events
- `id` - Primary key
- `event_type` - Event type (VEHICLE_DETECTED, NO_VEHICLE)
- `distance` - Distance reading (optional)
- `timestamp` - Event timestamp

## Methods

- `add_vehicle(plate_number)` - Add vehicle to authorized list
- `remove_vehicle(plate_number)` - Remove vehicle from list
- `is_authorized(plate_number)` - Check authorization
- `get_all_vehicles()` - Get all authorized vehicles
- `log_detection_event(event_type, distance)` - Log detection event
- `get_recent_events(limit)` - Get recent detection events
