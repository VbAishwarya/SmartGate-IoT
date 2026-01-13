"""SmartGate-IoT Main Application - Main entry point for the vehicle entry system."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.vehicle_detection import VehicleDetector, MockSensor
from src.database import VehicleDB
from src.common import (
    Colors, print_event, print_header, print_success, print_info, 
    print_warning, print_error, ScenarioRunner
)
from src.common.commands import CommandHandler
from src.common.dashboard import start_dashboard


def initialize_system():
    """Initialize system components."""
    print_info("Initializing system components...")
    sensor = MockSensor(mode="manual")
    detector = VehicleDetector(sensor, threshold_cm=10.0)
    db = VehicleDB("smartgate.db")
    
    print_info("Setting up authorized vehicles...")
    for plate in ["ABC123", "XYZ789", "DEF456"]:
        db.add_vehicle(plate)
    print_success(f"3 vehicles authorized")
    
    def log_to_db(event):
        db.log_detection_event(event['type'], event['data'].get('distance'))
    
    detector.on_vehicle_detected(print_event)
    detector.on_vehicle_detected(log_to_db)
    detector.on_no_vehicle(print_event)
    detector.on_no_vehicle(log_to_db)
    
    return sensor, detector, db


def show_main_menu():
    """Display main menu."""
    print(f"\n{Colors.BOLD}Main Menu:{Colors.RESET}\n")
    menu_items = [
        ("1", "Run Scenario", "Choose and run a predefined scenario"),
        ("2", "Quick Test", "Test with distance input"),
        ("3", "System Status", "Show current system status"),
        ("4", "View Events", "Show recent detection events"),
        ("5", "View Vehicles", "List all authorized vehicles"),
        ("6", "Check Plate", "Check if plate is authorized"),
        ("7", "Web Dashboard", "Open web dashboard"),
        ("0", "Exit", "Exit application"),
    ]
    
    for key, title, desc in menu_items:
        print(f"  {Colors.CYAN}{key}.{Colors.RESET} {title:20s} - {Colors.DIM}{desc}{Colors.RESET}")


def main():
    """Main application loop."""
    print_header("SmartGate-IoT - Vehicle Entry System")
    
    sensor, detector, db = initialize_system()
    scenario_runner = ScenarioRunner(sensor, detector, db)
    command_handler = CommandHandler(sensor, detector, db)
    
    print_header("Vehicle Detection System Running")
    
    while True:
        try:
            show_main_menu()
            choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                scenario_runner.show_scenario_menu()
                scenario_choice = input(f"\n{Colors.CYAN}Select scenario: {Colors.RESET}").strip()
                scenarios = scenario_runner.get_available_scenarios()
                if scenario_choice in scenarios:
                    scenario_name, _ = scenarios[scenario_choice]
                    scenario_runner.run_scenario(scenario_name)
                elif scenario_choice == "0":
                    continue
                else:
                    print_error("Invalid scenario selection")
            elif choice == "2":
                distance = input(f"{Colors.CYAN}Enter distance (cm): {Colors.RESET}").strip()
                if distance.replace('.', '').isdigit():
                    command_handler.handle_distance(distance)
                else:
                    print_error("Invalid distance value")
            elif choice == "3":
                command_handler.handle_status()
            elif choice == "4":
                command_handler.handle_events()
            elif choice == "5":
                command_handler.handle_vehicles()
            elif choice == "6":
                plate = input(f"{Colors.CYAN}Enter plate number: {Colors.RESET}").strip()
                if plate:
                    command_handler.handle_check(plate)
                else:
                    print_warning("No plate number provided")
            elif choice == "7":
                print_info("Starting web dashboard...")
                print_info("Dashboard will be available at: http://localhost:5000")
                print_warning("Press Ctrl+C in the dashboard terminal to stop")
                start_dashboard(db)
            else:
                print_warning("Invalid option. Please select a number from the menu.")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Exiting...{Colors.RESET}")
            break
        except Exception as e:
            print_error(f"Error: {e}")
    
    print_header("System Shutdown Complete")


if __name__ == "__main__":
    main()
