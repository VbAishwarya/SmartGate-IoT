# OCR with Database (Hima & Dhruvi)

This folder is **contrib** (hardware) content. In the project’s docs it’s referred to as **contrib/ocr_with_database**.

## Contents

| File | Purpose |
|------|--------|
| **Servo_led_test.py** | Standalone hardware test: ultrasonic (GPIO 23/24), LEDs (17/27), servo (18). Opens gate when object &lt; 10 cm. Uses `RPi.GPIO`. No camera/OCR. |
| **Ocr.py** | Full pipeline: camera (Picamera2), ultrasonic, LEDs, servo + OCR. Authorized plates from **text file** `authorized_plates.txt`. Exact match only. |
| **Database_Ocr_test.py** | Same pipeline + **SQLite** `plates.db`; exact match on `authorized_plates` table. |
| **Smart_gate_with_DB.py** | Full version: SQLite + **fuzzy matching** (95%), live preview, 5 s gate-open window, log to `gate_log2.txt`. Stops after first authorized vehicle. |

## Requirements

- **Raspberry Pi** with GPIO, camera, ultrasonic sensor, servo, LEDs.
- Python packages: `gpiozero`, `picamera2`, `PIL`, `pytesseract`, `opencv-python`, `numpy`. For `Servo_led_test.py`: `RPi.GPIO` only.

## Relation to main app

- **main.py** uses a **mock sensor** and `src/database/VehicleDB`; it does not use camera or GPIO and runs without hardware.
- These scripts are the **real-hardware** counterpart: same ideas (distance, OCR, DB, fuzzy match) but tied to RPi and camera.
- The main app’s **VehicleDB** and **fuzzy logic** live in `src/database/` and `src/fuzzy_logic.py`; these scripts use their own DB path (`plates.db`) and logic for device use.

## Naming

This directory is **contrib/ocr_with_database**. See `contrib/README.md` and `docs/ARCHITECTURE.md` for conventions.
