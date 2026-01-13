# SmartGate-IoT
IoT-based Automated Vehicle Entry System (Interdisciplinary Project WS25/26)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Project Overview
SmartGate-IoT is a scaled IoT demonstration project that showcases an automated vehicle entry system using sensing, camera-based recognition, and barrier actuation.

## 📚 Project Documentation

### Documentation
- **[Vehicle Detection Logic](docs/vehicle_detection_logic.md)** - Detection logic and pseudocode
- **[Assumptions](docs/assumptions.md)** - Assumptions and constraints

### Current Status
- ✅ **Vehicle Detection Module:** Complete
- ✅ **Database Module:** Complete (SQLite with fuzzy matching)
- ✅ **Web Dashboard:** Complete (Flask-based)
- ✅ **Menu-Driven Interface:** Complete (scenario-focused)
- ⏳ **Image Capture Module:** Not started
- ⏳ **OCR Module:** Not started
- ⏳ **Barrier Control Module:** Not started

## 🔗 Important Links
- 📄 Project Documentation (Confluence): https://aishwaryavb.atlassian.net/wiki/spaces/IP/overview?homepageId=9437389
- 📋 Kanban Board (Jira): https://aishwaryavb.atlassian.net/jira/software/projects/KAN/boards/1
- ⏱ Timesheet: https://bildungsportal.sachsen.de/opal/auth/RepositoryEntry/51791953965/CourseNode/1630981630155929010/template-time-sheet.xlsx
- 🎤 Presentations & Slides: 
- 🧠 Architecture Diagrams (Miro / draw.io): 
- 📁 Shared Drive / Assets: https://docs.google.com/spreadsheets/d/19PhfY0BA-zd2jdC-9sQXwtUukbKMdTmX4n_z6MjDqkY/edit?gid=0#gid=0

## 🏗️ Project Structure

```
SmartGate-IoT/
├── config/              # Configuration files
├── src/                 # Source code
│   ├── vehicle_detection/  # ✅ Vehicle detection module
│   ├── database/           # ✅ SQLite database module
│   ├── common/             # ✅ Shared utilities (colors, commands, scenarios)
│   ├── image_capture/      # Future
│   ├── ocr/                # Future
│   ├── barrier_control/    # Future
│   └── __init__.py
├── tests/              # Test files
├── docs/               # Documentation
├── examples/           # Demo scripts
├── templates/          # Web dashboard templates
├── main.py             # Main application entry point
└── run_dashboard.py    # Standalone dashboard runner
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/SmartGate-IoT.git
   cd SmartGate-IoT
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

### Using the Application

- Select `1` to run scenarios
- Choose from 9 predefined scenarios
- For custom plate testing, select scenario `8` and enter your plate number

See [SETUP.md](SETUP.md) for detailed setup instructions.

## 🎮 Main Menu Options

| Option | Description |
|--------|-------------|
| `1` | **Run Scenario** - Choose and run a predefined scenario |
| `2` | **Quick Test** - Test with distance input |
| `3` | **System Status** - Show current system status |
| `4` | **View Events** - Show recent detection events |
| `5` | **View Vehicles** - List all authorized vehicles |
| `6` | **Check Plate** - Check if plate is authorized (with fuzzy matching) |
| `7` | **Web Dashboard** - Open web dashboard at http://localhost:5000 |
| `0` | **Exit** - Exit application |

## 📋 Available Scenarios

1. **Quick vehicle pass** - Fast vehicle passing through
2. **Slow vehicle approach** - Gradual vehicle approach
3. **Vehicle stops at gate** - Vehicle stops and waits
4. **Multiple vehicles sequence** - Multiple vehicles in sequence
5. **False alarm test** - Near-threshold readings test
6. **Full flow - Authorized vehicle** - Complete flow with authorized plate
7. **Full flow - Unauthorized vehicle** - Complete flow with denied plate
8. **Full flow - Custom plate number** - Enter your own plate number
9. **Full flow - Multiple vehicles** - Multiple vehicles with different plates

## 💡 Usage Examples

### Run a Scenario
```
Select option: 1
Select scenario: 6
```
Runs the "Full flow - Authorized vehicle" scenario automatically.

### Test Custom Plate
```
Select option: 1
Select scenario: 8
Enter license plate number: MYPLATE123
```
Runs full flow scenario with your custom plate number and shows authorization result.

### Quick Distance Test
```
Select option: 2
Enter distance (cm): 8.5
```
Tests detection with a specific distance value.

## 🌐 Web Dashboard

Access the web dashboard:
- From main menu: Select option `7`
- Standalone: `python run_dashboard.py`
- URL: http://localhost:5000

Features:
- Real-time event display
- Statistics (total events, authorized vehicles, detections)
- Auto-refresh every 5 seconds
- Responsive design

## 🧪 Testing

Run tests:
```bash
python tests/test_detector.py
python tests/test_database.py
```

Run demo scripts:
```bash
python examples/demo_detection.py
python examples/demo_database.py
python examples/demo_integration.py
```

## 📝 Module Development

The project follows a modular architecture:
- **Common utilities** in `src/common/` (colors, commands, scenarios, dashboard)
- **Vehicle detection** in `src/vehicle_detection/`
- **Database** in `src/database/`

Each module is independently testable and follows consistent patterns.

## 🔧 Configuration

Edit `config/detection_config.yaml` to adjust:
- Detection threshold (default: 10cm)
- Sensor reading bounds
- Polling interval

## 📦 Dependencies

- Python 3.11+
- pyyaml>=6.0
- flask>=3.0.0 (for web dashboard)

## 🎯 Key Features

- ✅ Menu-driven interface (no need to type commands)
- ✅ 9 predefined scenarios including full flow tests
- ✅ Custom plate number input for testing
- ✅ Real-time event logging to database
- ✅ Fuzzy matching for license plates
- ✅ Web dashboard for monitoring
- ✅ Color-coded terminal output
- ✅ Modular, maintainable code structure

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Driver:** @Aishwarya V B
- **Approver:** Prof. Christian Fiedler
- **Contributors:** @Yash Kakadiya, @Dishva Italiya, @Jenish Sheladiya, @dhruvimoradiya01, @HimaPatel24, @Shubha, @pavanmgowda2497, @gourip682

---

**Status:** ✅ Vehicle Detection & Database modules complete  
**Next Steps:** Image Capture, OCR, Barrier Control modules
