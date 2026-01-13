# Setup Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

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

4. **Verify installation:**
   ```bash
   python main.py
   ```

## Configuration

Edit `config/detection_config.yaml` to customize:
- Detection threshold (default: 10cm)
- Sensor reading bounds
- Polling interval

## Running Tests

```bash
python tests/test_detector.py
python tests/test_database.py
```

## Running Demos

```bash
python examples/demo_detection.py
python examples/demo_database.py
python examples/demo_integration.py
```

## Troubleshooting

**Import errors:**
- Ensure you're in the project root directory
- Verify virtual environment is activated
- Check that all dependencies are installed

**Database errors:**
- Database files are created automatically
- Check file permissions in project directory

**Flask not found:**
- Install with: `pip install flask`
