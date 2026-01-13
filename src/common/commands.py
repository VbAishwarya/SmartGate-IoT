"""Command handlers for main application."""

import time
from src.vehicle_detection import MockSensor, VehicleDetector
from src.vehicle_detection.detector import VEHICLE_DETECTED
from src.database import VehicleDB
from .colors import Colors, print_info, print_success, print_warning, print_error


class CommandHandler:
    """Handles user commands."""
    
    def __init__(self, sensor: MockSensor, detector: VehicleDetector, db: VehicleDB):
        self.sensor = sensor
        self.detector = detector
        self.db = db
    
    def handle_status(self):
        """Show system status."""
        print(f"\n{Colors.BOLD}System Status:{Colors.RESET}\n")
        state_color = Colors.GREEN if self.detector.current_state == VEHICLE_DETECTED else Colors.DIM
        print(f"  State:     {state_color}{self.detector.current_state}{Colors.RESET}")
        print(f"  Threshold: {Colors.CYAN}{self.detector.threshold_cm}cm{Colors.RESET}")
        print(f"  Distance:  {Colors.CYAN}{self.sensor.get_distance():.1f}cm{Colors.RESET}")
    
    def handle_events(self):
        """Show recent detection events."""
        events = self.db.get_recent_events(limit=10)
        print(f"\n{Colors.BOLD}Recent Detection Events ({len(events)}):{Colors.RESET}\n")
        if events:
            print(f"  {Colors.DIM}{'Event Type':<20} {'Distance':<12} {'Timestamp':<20}{Colors.RESET}")
            print(f"  {Colors.DIM}{'-'*52}{Colors.RESET}")
            for event in events:
                dist_str = f"{event['distance']:.1f}cm" if event['distance'] else "N/A"
                event_color = Colors.GREEN if event['event_type'] == VEHICLE_DETECTED else Colors.DIM
                print(f"  {event_color}{event['event_type']:<20}{Colors.RESET} "
                      f"{Colors.CYAN}{dist_str:<12}{Colors.RESET} "
                      f"{Colors.DIM}{event['timestamp']}{Colors.RESET}")
        else:
            print_warning("No events found")
    
    def handle_vehicles(self):
        """List authorized vehicles."""
        vehicles = self.db.get_all_vehicles()
        print(f"\n{Colors.BOLD}Authorized Vehicles ({len(vehicles)}):{Colors.RESET}\n")
        if vehicles:
            for i, v in enumerate(vehicles, 1):
                print(f"  {Colors.CYAN}{i}.{Colors.RESET} {Colors.GREEN}{v['plate_number']}{Colors.RESET} "
                      f"{Colors.DIM}(Added: {v['created_at']}){Colors.RESET}")
        else:
            print_warning("No authorized vehicles")
    
    def handle_check(self, plate: str):
        """Check if plate is authorized."""
        plate = plate.strip().upper()
        if self.db.is_authorized(plate):
            print_success(f"'{plate}' is authorized")
        else:
            matches = self.db.find_similar_plates(plate, threshold=0.85)
            if matches:
                print_warning(f"'{plate}' is not authorized, but similar plates found:")
                for match, similarity in matches:
                    print(f"  {Colors.CYAN}{match}{Colors.RESET} (similarity: {similarity:.1%})")
            else:
                print_error(f"'{plate}' is not authorized")
    
    def handle_approach(self):
        """Simulate vehicle approaching."""
        print_info("Simulating vehicle approach...")
        for dist in [50, 30, 15, 8, 5]:
            self.sensor.set_distance(dist)
            self.detector.check()
            time.sleep(0.3)
    
    def handle_depart(self):
        """Simulate vehicle departing."""
        print_info("Simulating vehicle departure...")
        for dist in [5, 12, 25, 40, 60]:
            self.sensor.set_distance(dist)
            self.detector.check()
            time.sleep(0.3)
    
    def handle_distance(self, distance_str: str):
        """Handle distance input."""
        try:
            distance = float(distance_str)
            self.sensor.set_distance(distance)
            self.detector.check()
        except ValueError:
            print_error("Invalid distance value")
