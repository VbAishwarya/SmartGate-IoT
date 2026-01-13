"""Scenario runner with interactive plate input support."""

import time
from src.vehicle_detection import MockSensor, VehicleDetector
from src.vehicle_detection.detector import VEHICLE_DETECTED
from src.database import VehicleDB
from .colors import Colors, print_info, print_warning


class ScenarioRunner:
    """Handles scenario execution with interactive features."""
    
    def __init__(self, sensor: MockSensor, detector: VehicleDetector, db: VehicleDB = None):
        self.sensor = sensor
        self.detector = detector
        self.db = db
    
    def get_available_scenarios(self):
        """Get list of available scenarios."""
        return {
            "1": ("quick_pass", "Quick vehicle pass"),
            "2": ("slow_approach", "Slow vehicle approach"),
            "3": ("stop_and_go", "Vehicle stops at gate"),
            "4": ("multiple_vehicles", "Multiple vehicles sequence"),
            "5": ("false_alarm", "False alarm test"),
            "6": ("full_flow_authorized", "Full flow - Authorized vehicle"),
            "7": ("full_flow_denied", "Full flow - Unauthorized vehicle"),
            "8": ("full_flow_custom", "Full flow - Custom plate number"),
            "9": ("full_flow_multiple", "Full flow - Multiple vehicles"),
        }
    
    def show_scenario_menu(self):
        """Display scenario selection menu."""
        print(f"\n{Colors.BOLD}Available Scenarios:{Colors.RESET}\n")
        scenarios = self.get_available_scenarios()
        for key, (name, desc) in scenarios.items():
            print(f"  {Colors.CYAN}{key}.{Colors.RESET} {desc}")
        print(f"  {Colors.CYAN}0.{Colors.RESET} Back to main menu")
    
    def run_scenario(self, scenario_name: str, custom_plate: str = None):
        """Run a predefined scenario."""
        if scenario_name == "full_flow_custom":
            if not custom_plate:
                custom_plate = input(f"\n{Colors.CYAN}Enter license plate number: {Colors.RESET}").strip().upper()
                if not custom_plate:
                    print_warning("No plate number provided, using default")
                    custom_plate = "CUSTOM123"
            scenario = self._create_custom_full_flow_scenario(custom_plate)
        else:
            scenario = self.sensor.get_predefined_scenario(scenario_name)
        
        if not scenario:
            print_error(f"Unknown scenario: {scenario_name}")
            return
        
        is_full_flow = scenario_name.startswith("full_flow")
        print_info(f"Running scenario: {scenario_name} ({len(scenario)} steps)")
        
        if is_full_flow:
            print(f"{Colors.DIM}  Step | Distance | Detection | Plate      | Authorization | Gate{Colors.RESET}")
            print(f"{Colors.DIM}  {'-'*75}{Colors.RESET}")
        else:
            print(f"{Colors.DIM}  Step | Distance | Threshold | State Change{Colors.RESET}")
            print(f"{Colors.DIM}  {'-'*55}{Colors.RESET}")
        
        for i, step in enumerate(scenario, 1):
            distance = step['distance']
            delay = step.get('delay', 0.3)
            plate = step.get('plate') or custom_plate
            
            self.sensor.set_distance(distance)
            event = self.detector.check()
            
            if is_full_flow:
                self._print_full_flow_step(i, distance, plate, event)
            else:
                self._print_simple_step(i, distance, event)
            
            time.sleep(delay)
        
        print(f"{Colors.DIM}  {'-'*(75 if is_full_flow else 55)}{Colors.RESET}\n")
    
    def _create_custom_full_flow_scenario(self, plate: str):
        """Create custom full flow scenario with user-provided plate."""
        return [
            {"distance": 50, "delay": 0.3, "plate": plate},
            {"distance": 30, "delay": 0.3, "plate": plate},
            {"distance": 15, "delay": 0.3, "plate": plate},
            {"distance": 8, "delay": 0.5, "plate": plate},
            {"distance": 5, "delay": 1.0, "plate": plate},
            {"distance": 12, "delay": 0.3, "plate": plate},
            {"distance": 30, "delay": 0.3, "plate": plate},
            {"distance": 50, "delay": 0.3, "plate": plate},
        ]
    
    def _print_full_flow_step(self, step_num: int, distance: float, plate: str, event: str):
        """Print full flow scenario step."""
        is_detected = distance < self.detector.threshold_cm
        
        if is_detected:
            detection_status = f"{Colors.GREEN}✓ Detected{Colors.RESET}"
            if plate and self.db:
                plate_status = plate
                if self.db.is_authorized(plate):
                    auth_status = f"{Colors.GREEN}✓ Authorized{Colors.RESET}"
                    gate_status = f"{Colors.GREEN}OPEN{Colors.RESET}"
                else:
                    auth_status = f"{Colors.RED}✗ Denied{Colors.RESET}"
                    gate_status = f"{Colors.RED}CLOSED{Colors.RESET}"
            else:
                plate_status = f"{Colors.DIM}{plate or 'No plate'}{Colors.RESET}"
                auth_status = f"{Colors.DIM}N/A{Colors.RESET}"
                gate_status = f"{Colors.DIM}N/A{Colors.RESET}"
        else:
            detection_status = f"{Colors.DIM}No vehicle{Colors.RESET}"
            plate_status = auth_status = gate_status = f"{Colors.DIM}-{Colors.RESET}"
        
        print(f"  {step_num:2d}  | {distance:6.1f}cm | {detection_status:10s} | {plate_status:10s} | {auth_status:13s} | {gate_status}")
    
    def _print_simple_step(self, step_num: int, distance: float, event: str):
        """Print simple detection scenario step."""
        state_change = f" → {Colors.GREEN if event == VEHICLE_DETECTED else Colors.DIM}{event}{Colors.RESET}" if event else ""
        threshold_status = f"{Colors.GREEN}✓ Below{Colors.RESET}" if distance < self.detector.threshold_cm else f"{Colors.DIM}✗ Above{Colors.RESET}"
        print(f"  {step_num:2d}  | {distance:6.1f}cm | {threshold_status:12s} | {self.detector.current_state}{state_change}")
