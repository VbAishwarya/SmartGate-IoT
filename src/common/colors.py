"""Terminal color formatting utilities."""

from src.vehicle_detection.detector import VEHICLE_DETECTED, NO_VEHICLE


class Colors:
    """ANSI color codes for terminal formatting."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    DIM = '\033[2m'


def print_event(event):
    """Print event with enhanced formatting."""
    event_type = event['type']
    timestamp = event['timestamp'].split('T')[1].split('.')[0]
    distance = event['data'].get('distance', 'N/A')
    
    if event_type == VEHICLE_DETECTED:
        print(f"{Colors.GREEN}{Colors.BOLD}🚗 [{timestamp}]{Colors.RESET} "
              f"{Colors.GREEN}VEHICLE_DETECTED{Colors.RESET} - "
              f"{Colors.CYAN}Distance: {distance:.1f}cm{Colors.RESET}")
    else:
        print(f"{Colors.DIM}   [{timestamp}]{Colors.RESET} "
              f"{Colors.DIM}NO_VEHICLE{Colors.RESET} - "
              f"{Colors.DIM}Distance: {distance:.1f}cm{Colors.RESET}")


def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")
