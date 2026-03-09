# OCR with Database (contrib)

Alternate RPi pipeline (camera, ultrasonic, servo, LEDs, OCR, SQLite). Run on device.

| File | Purpose |
|------|---------|
| **Servo_led_test.py** | Hardware test: ultrasonic (23/24), LEDs (17/27), servo (18). No camera/OCR. |
| **Ocr.py** | Camera + ultrasonic + LEDs + servo + OCR. Authorized plates from `authorized_plates.txt`. |
| **Database_Ocr_test.py** | Same + SQLite `plates.db` (exact match). |
| **Smart_gate_with_DB.py** | SQLite + fuzzy matching (95%), live preview, gate log. |

For the **recommended Pi demo** using shared gate logic, use **rpi/alpr.py** and run `python alpr.py` from project root. See [README.md](../../README.md) and [SETUP.md](../../SETUP.md).
