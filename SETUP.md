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

All tests use a **mock sensor** and **temporary database**; no hardware is required.

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run full suite (unit + integration + e2e)
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

Legacy script-style tests (still supported):

```bash
python tests/test_detector.py
python tests/test_database.py
```

### Vision tests (optional)

Vision tests run **plate OCR** on real images and **skip** if dependencies are missing. The same OCR is used by the dashboard’s “Plate check (image upload)” feature.

**1. Install system Tesseract** (required for OCR; run in your terminal):

```bash
# Fedora / RHEL
sudo dnf install tesseract

# Debian / Ubuntu
sudo apt-get install tesseract-ocr
```

**2. Install Python packages:**

```bash
pip install -r requirements-vision.txt
```

**3. Run vision tests** (uses images in contrib/image_processing_ocr/number_plates/ or tests/data/images/):

```bash
# Use the same Python that has the vision packages (recommended)
python3 -m pytest tests/vision/ -v
# Or, if your default pytest uses that Python:
pytest tests/vision/ -v
```

If the test is skipped with "pytesseract not installed" or "OCR failed", ensure both the **system** Tesseract and the **Python** packages are installed for the same Python you use to run pytest (e.g. `python3 -m pip install -r requirements-vision.txt` then `python3 -m pytest tests/vision/ -v`).

**Dashboard plate check:** To use "Plate check (image upload)" in the web dashboard, install the same vision dependencies (Tesseract + `requirements-vision.txt`). Without them, the dashboard still works but the plate-check endpoint will return "OCR not available".

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
