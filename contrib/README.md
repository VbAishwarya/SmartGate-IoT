# Contrib – hardware and experimental code

All hardware-specific and experimental modules live here. Directory names use **lowercase_with_underscores**.

## Modules

| Directory | Description |
|-----------|-------------|
| **image_processing_ocr/** | OCR notebook (Colab-friendly) and sample number plate images in `number_plates/`. Used by vision tests when available. |
| **ocr_with_database/** | RPi pipeline: camera, ultrasonic, servo, LEDs, OCR, SQLite. Scripts: `Servo_led_test.py`, `Ocr.py`, `Database_Ocr_test.py`, `Smart_gate_with_DB.py`. Run on device. |

Each module has its own **README.md**. The main application (`main.py`) does not depend on these and runs without hardware.

See [ARCHITECTURE.md](../docs/ARCHITECTURE.md) for the overall design and naming conventions.
