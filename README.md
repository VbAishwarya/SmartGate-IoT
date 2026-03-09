# SmartGate-IoT
IoT-based Automated Vehicle Entry System (Interdisciplinary Project WS25/26)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Project Overview
SmartGate-IoT is a scaled IoT demonstration project that showcases an automated vehicle entry system using sensing, camera-based recognition, and barrier actuation.

## 📚 Project Documentation

### Documentation
- **[Docs index](docs/README.md)** — Overview of all documentation
- **[Architecture](docs/ARCHITECTURE.md)** — Design (Ports & Adapters), directory layout
- **[Setup](SETUP.md)** — Installation, tests, vision, Raspberry Pi
- **[Testing](docs/TESTING.md)** — Test layers, vision tests, dashboard
- **[Design](docs/DESIGN.md)** — Assumptions, detection logic, constraints
- **[Module reference](docs/MODULES.md)** — Database, vehicle detection, vision (OCR)
- **[Plate OCR options](docs/PLATE_OCR_OPTIONS.md)** — Tesseract, EasyOCR, PaddleOCR, ALPR

### Current Status
- ✅ **Vehicle Detection Module:** Complete
- ✅ **Database Module:** Complete (SQLite with fuzzy matching)
- ✅ **Web Dashboard:** Complete (Flask-based; run scenarios, plate check via image upload)
- ✅ **Menu-Driven Interface:** Complete (scenario-focused)
- ✅ **Vision/OCR (optional):** Shared plate OCR in `src/vision/`; used by vision tests and dashboard image upload
- ⏳ **Image Capture Module:** Not started
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
├── config/                 # Configuration files
├── src/                    # Source code (see docs/ARCHITECTURE.md)
│   ├── core/               # Ports (interfaces): DistanceSensor, PlateStorage
│   ├── vehicle_detection/  # ✅ Vehicle detection (detector + mock sensor)
│   ├── database/           # ✅ SQLite database module
│   ├── common/             # ✅ Shared utilities (colors, commands, scenarios, dashboard)
│   ├── fuzzy_logic.py      # ✅ Fuzzy plate matching (optical typo rules)
│   ├── vision/             # ✅ Optional: plate OCR (used by tests + dashboard image upload)
│   ├── image_capture/      # Future
│   ├── ocr/                # Future
│   ├── barrier_control/   # Future
│   └── __init__.py
├── tests/                  # Test suite (no hardware required)
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── e2e/                # End-to-end tests
│   ├── vision/             # Optional: OCR/ML tests with real images (see docs/TESTING.md)
│   ├── data/               # Fixtures: images/, videos/ for vision tests
│   ├── conftest.py         # Shared pytest fixtures
│   ├── test_detector.py    # Legacy detector tests
│   └── test_database.py    # Legacy database tests
├── contrib/                # Hardware and experimental modules
│   ├── image_processing_ocr/   # OCR notebook + sample plates (number_plates/)
│   ├── ocr_with_database/     # Alternate RPi pipeline (camera, servo, LEDs, OCR, SQLite)
│   └── README.md
├── rpi/                    # Raspberry Pi demonstration (camera, GPIO, gate)
│   └── alpr.py             # Pi entry: Picamera2, ultrasonic, servo, LEDs, plate OCR, gate logic
├── docs/                   # Documentation
├── examples/               # Demo scripts
├── templates/              # Web dashboard templates
├── main.py                 # Main application entry point
├── run_dashboard.py        # Standalone dashboard runner
├── alpr.py                 # Pi demo launcher (runs rpi/alpr.py; use on device only)
├── run_gate_dashboard.py   # Gate Live dashboard (port 5001; Pi pushes events here)
```

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VbAishwarya/SmartGate-IoT.git
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

### Contrib / hardware modules

Hardware and experimental code lives under **contrib/** and **rpi/**:

| Folder | Purpose |
|--------|--------|
| **[rpi/](rpi/)** | **Raspberry Pi demonstration:** camera (Picamera2), ultrasonic, servo, LEDs, plate OCR, gate open/close. Run from project root: `python alpr.py`. Uses `src.common.gate_logic.decide_gate_action` and shared fuzzy logic. Requires Pi with gpiozero, picamera2, tesseract, opencv. |
| **[contrib/image_processing_ocr/](contrib/image_processing_ocr/)** | OCR notebook (Colab-friendly) and sample plate images in `number_plates/`. Vision tests use these when available. |
| **[contrib/ocr_with_database/](contrib/ocr_with_database/)** | Alternate RPi pipeline: camera, ultrasonic, servo, LEDs, OCR, SQLite. Scripts: `Servo_led_test.py`, `Ocr.py`, `Smart_gate_with_DB.py`. Run on device. |

The root **alpr.py** is a launcher that runs **rpi/alpr.py** so you can start the Pi demo with `python alpr.py` from the project root. The main app (`main.py`) does not depend on these; it uses a mock sensor and runs without hardware.

### Development without hardware

The application and **entire test suite** run without Raspberry Pi or sensors. The main app uses a **mock distance sensor** (`MockSensor`); you can run scenarios and use the menu as usual. To run tests: `pytest tests/ -v` (see [Testing](#-testing)).

### Raspberry Pi demonstration

On a Raspberry Pi with camera, ultrasonic sensor, servo, and LEDs installed, run the gate demo from the **project root**:

```bash
python alpr.py
```

This runs **rpi/alpr.py**: captures frames with Picamera2, runs plate OCR (Tesseract), checks plates against a local SQLite DB (`plates.db`) with fuzzy matching, and opens/closes the gate via servo. Install on the Pi: `gpiozero`, `picamera2`, `opencv-python`, `pytesseract`, system Tesseract. See [SETUP.md](SETUP.md) for Pi setup.

#### Gate Live Dashboard (for presentations)

To show Pi events **live on a separate dashboard** (e.g. on a laptop during a demo):

1. On the **laptop** (same network as the Pi), start the Gate Live dashboard:
   ```bash
   python run_gate_dashboard.py
   ```
   Opens at **http://localhost:5001** — clean, dark UI with current plate, distance, decision, gate state, and event log.

2. On the **Pi**, set the dashboard URL and run the gate:
   ```bash
   export GATE_DASHBOARD_URL=http://<laptop-ip>:5001
   python alpr.py
   ```
   The Pi posts each plate decision and gate open/close to the dashboard; the page auto-refreshes every 1.5s. The main dashboard (port 5000) is unchanged.

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
- **Real-time event display** — Stats (total events, authorized vehicles, detections) and events table; **fetch-based refresh** (no full page reload) with configurable interval and **Pause auto-refresh** toggle.
- **Run scenarios** — Each scenario has a **Run** button; runs the scenario (mock sensor + detector), logs events to the database, then you can refresh to see new events.
- **Plate check (image upload)** — Upload a license plate image (JPEG/PNG); the server runs **plate OCR** (Tesseract via `src/vision`) and checks the read text against authorized vehicles (exact + fuzzy match). Shows read plate, authorized/denied, and similar plates. Requires optional vision dependencies (see SETUP.md).
- **API:** `GET /api/events`, `GET /api/vehicles`, `GET /api/scenarios`; `POST /api/scenarios/<id>/run`; `POST /api/vision/check` (multipart image upload).

## 🧪 Testing

All tests run **without hardware**: they use a mock sensor, temporary databases, and no camera/GPIO.

### Run the full test suite

```bash
# Install test dependencies (optional; pytest may already be installed)
pip install -r requirements-dev.txt

# Run all tests (unit, integration, e2e)
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Test layers

| Layer | Location | Description |
|-------|----------|-------------|
| **Unit** | `tests/unit/` | Detector, database, fuzzy logic, scenario runner, command handler (mocked deps) |
| **Integration** | `tests/integration/` | Detector + DB logging; scenario flow with real components |
| **E2E** | `tests/e2e/` | Full flow: init, scenario run, DB state and plate check (no interactive input) |

Optional **vision** tests (real images/OCR): `tests/vision/`. They use the shared **`src/vision`** module when available (plate OCR). They skip if no image or OCR deps. See [docs/TESTING.md](docs/TESTING.md).

### Run specific test groups

```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
pytest tests/unit/test_detector.py -v
```

Optional: run vision tests (use real images in `contrib/image_processing_ocr/number_plates/` or `tests/data/images/`; requires optional `pytesseract`/OpenCV):

```bash
pytest tests/vision/ -v
```

### Legacy script-style tests (still supported)

```bash
python tests/test_detector.py
python tests/test_database.py
```

### Run demo scripts

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

For development and testing:
- pytest>=7.0.0, pytest-cov>=4.0.0 (see `requirements-dev.txt`)

## 🎯 Key Features

- ✅ Menu-driven interface (no need to type commands)
- ✅ 9 predefined scenarios including full flow tests
- ✅ Custom plate number input for testing
- ✅ Real-time event logging to database
- ✅ Fuzzy matching for license plates
- ✅ Web dashboard for monitoring
- ✅ Color-coded terminal output
- ✅ Modular, maintainable code structure
- ✅ **Full test suite without hardware** (unit, integration, E2E with mock sensor and temp DB)
- ✅ **Dashboard:** run scenarios from UI, plate check via image upload (OCR), fetch-based refresh with pause
- ✅ **Shared plate OCR** (`src/vision/`) for tests and dashboard

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
