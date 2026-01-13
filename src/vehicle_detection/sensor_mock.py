"""Mock Sensor Generator - Generates mock distance readings for vehicle detection testing."""

import random
from typing import Optional, List, Dict


class MockSensor:
    """Mock sensor that generates distance readings in centimeters."""
    
    def __init__(self, mode: str = "manual"):
        self.mode = mode
        self.current_distance = 50.0
        self.scenario_index = 0
        self.scenario_data: List[Dict] = []
    
    def get_distance(self) -> float:
        """Get current distance reading in centimeters."""
        if self.mode == "random":
            return random.uniform(2.0, 100.0)
        elif self.mode == "scenario":
            return self._get_scenario_distance()
        return self.current_distance
    
    def set_distance(self, distance: float):
        """Manually set distance (for manual mode)."""
        self.current_distance = distance
    
    def set_mode(self, mode: str):
        """Change sensor mode."""
        self.mode = mode
    
    def set_scenario(self, scenario: List[Dict]):
        """Set scenario data for scenario mode."""
        self.scenario_data = scenario
        self.scenario_index = 0
    
    def _get_scenario_distance(self) -> float:
        """Get next distance from scenario."""
        if not self.scenario_data:
            return 50.0
        
        if self.scenario_index < len(self.scenario_data):
            distance = self.scenario_data[self.scenario_index]['distance']
            self.scenario_index += 1
            return distance
        return self.scenario_data[-1]['distance']
    
    def simulate_vehicle_approach(self):
        """Simulate vehicle approaching (decreasing distance)."""
        if self.current_distance > 5:
            self.current_distance -= 5
    
    def simulate_vehicle_departure(self):
        """Simulate vehicle leaving (increasing distance)."""
        if self.current_distance < 100:
            self.current_distance += 5
    
    def get_predefined_scenario(self, name: str) -> Optional[List[Dict]]:
        """Get predefined scenario by name."""
        scenarios = {
            "quick_pass": [
                {"distance": 50, "delay": 0.1}, {"distance": 30, "delay": 0.1},
                {"distance": 8, "delay": 0.2}, {"distance": 5, "delay": 0.2},
                {"distance": 12, "delay": 0.1}, {"distance": 30, "delay": 0.1},
                {"distance": 50, "delay": 0.1},
            ],
            "slow_approach": [
                {"distance": 100, "delay": 0.5}, {"distance": 80, "delay": 0.5},
                {"distance": 60, "delay": 0.5}, {"distance": 40, "delay": 0.5},
                {"distance": 25, "delay": 0.5}, {"distance": 15, "delay": 0.5},
                {"distance": 9, "delay": 1.0}, {"distance": 7, "delay": 1.0},
                {"distance": 6, "delay": 2.0},
            ],
            "stop_and_go": [
                {"distance": 50, "delay": 0.3}, {"distance": 30, "delay": 0.3},
                {"distance": 12, "delay": 0.3}, {"distance": 8, "delay": 2.0},
                {"distance": 7, "delay": 2.0}, {"distance": 8, "delay": 1.0},
                {"distance": 15, "delay": 0.5}, {"distance": 30, "delay": 0.5},
                {"distance": 50, "delay": 0.5},
            ],
            "multiple_vehicles": [
                {"distance": 50, "delay": 0.2}, {"distance": 8, "delay": 0.5},
                {"distance": 25, "delay": 0.3}, {"distance": 7, "delay": 0.5},
                {"distance": 20, "delay": 0.3}, {"distance": 9, "delay": 0.5},
                {"distance": 30, "delay": 0.3}, {"distance": 50, "delay": 0.2},
            ],
            "false_alarm": [
                {"distance": 50, "delay": 0.2}, {"distance": 12, "delay": 0.2},
                {"distance": 9, "delay": 0.2}, {"distance": 11, "delay": 0.2},
                {"distance": 50, "delay": 0.2},
            ],
            "full_flow_authorized": [
                {"distance": 50, "delay": 0.3, "plate": "ABC123"},
                {"distance": 30, "delay": 0.3, "plate": "ABC123"},
                {"distance": 15, "delay": 0.3, "plate": "ABC123"},
                {"distance": 8, "delay": 0.5, "plate": "ABC123"},
                {"distance": 5, "delay": 1.0, "plate": "ABC123"},
                {"distance": 12, "delay": 0.3, "plate": "ABC123"},
                {"distance": 30, "delay": 0.3, "plate": "ABC123"},
                {"distance": 50, "delay": 0.3, "plate": "ABC123"},
            ],
            "full_flow_denied": [
                {"distance": 50, "delay": 0.3, "plate": "UNAUTHORIZED"},
                {"distance": 30, "delay": 0.3, "plate": "UNAUTHORIZED"},
                {"distance": 15, "delay": 0.3, "plate": "UNAUTHORIZED"},
                {"distance": 8, "delay": 0.5, "plate": "UNAUTHORIZED"},
                {"distance": 8, "delay": 1.0, "plate": "UNAUTHORIZED"},
                {"distance": 15, "delay": 0.3, "plate": "UNAUTHORIZED"},
                {"distance": 30, "delay": 0.3, "plate": "UNAUTHORIZED"},
                {"distance": 50, "delay": 0.3, "plate": "UNAUTHORIZED"},
            ],
            "full_flow_multiple": [
                {"distance": 50, "delay": 0.2, "plate": "ABC123"},
                {"distance": 8, "delay": 0.5, "plate": "ABC123"},
                {"distance": 25, "delay": 0.2, "plate": "XYZ789"},
                {"distance": 7, "delay": 0.5, "plate": "XYZ789"},
                {"distance": 20, "delay": 0.2, "plate": "UNAUTHORIZED"},
                {"distance": 9, "delay": 0.5, "plate": "UNAUTHORIZED"},
                {"distance": 30, "delay": 0.2, "plate": None},
                {"distance": 50, "delay": 0.2, "plate": None},
            ],
        }
        return scenarios.get(name.lower())
