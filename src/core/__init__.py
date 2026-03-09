"""
Core abstractions (ports) for SmartGate-IoT.

This package defines the interfaces that adapters implement. The application
(detector, scenario runner, command handler) depends on these abstractions
so that sensors and storage can be swapped (mock vs real hardware) without
changing business logic.
"""

from .protocols import DistanceSensor, PlateStorage

__all__ = ["DistanceSensor", "PlateStorage"]
