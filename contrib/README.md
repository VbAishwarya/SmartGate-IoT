# Contrib – hardware and experimental code

Optional modules; the main app (`main.py`) does not depend on them.

| Directory | Description |
|-----------|--------------|
| **image_processing_ocr/** | OCR notebook (Colab) and sample plate images in `number_plates/`. Vision tests use these when available. |
| **ocr_with_database/** | Alternate RPi pipeline: camera, ultrasonic, servo, LEDs, OCR, SQLite. Run on device. |

For the **recommended Raspberry Pi demo** (camera, GPIO, gate), use **rpi/alpr.py** and run `python alpr.py` from the project root. See [SETUP.md](../SETUP.md) and [README.md](../README.md).
