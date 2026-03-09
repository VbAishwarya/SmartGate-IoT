"""
Ports (interfaces) for SmartGate-IoT — Ports & Adapters (Hexagonal) design.

Implementations:
- DistanceSensor: src.vehicle_detection.sensor_mock.MockSensor (and future real sensor adapter)
- PlateStorage: src.database.vehicle_db.VehicleDB
"""

from typing import Protocol, List, Optional, Tuple


class DistanceSensor(Protocol):
    """Port for distance measurement (e.g. ultrasonic sensor)."""

    def get_distance(self) -> float:
        """Return current distance in centimeters."""
        ...

    def set_distance(self, distance: float) -> None:
        """Set distance (for mock/manual mode). Optional on real hardware."""
        ...


class PlateStorage(Protocol):
    """Port for authorized plates and event logging."""

    def is_authorized(self, plate_number: str) -> bool:
        """Return True if the plate is authorized."""
        ...

    def get_all_vehicles(self) -> List[dict]:
        """Return all authorized vehicles."""
        ...

    def add_vehicle(self, plate_number: str) -> bool:
        """Add a plate. Return True if added."""
        ...

    def remove_vehicle(self, plate_number: str) -> bool:
        """Remove a plate. Return True if removed."""
        ...

    def log_detection_event(self, event_type: str, distance: Optional[float] = None) -> None:
        """Log a detection event."""
        ...

    def get_recent_events(self, limit: int = 50) -> List[dict]:
        """Return recent detection events."""
        ...

    def find_similar_plates(
        self, plate_number: str, threshold: float = 0.85
    ) -> List[Tuple[str, float]]:
        """Return list of (plate, similarity) for fuzzy matching."""
        ...
