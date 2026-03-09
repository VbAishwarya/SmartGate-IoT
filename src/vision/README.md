# Vision / Plate OCR

Optional module for **license plate OCR** using Tesseract. Used by:

- **Vision tests** (`tests/vision/`) — `ocr_from_path(image_path)` on sample images
- **Dashboard** — `POST /api/vision/check` uses `ocr_from_bytes(data)` on uploaded images, then checks authorization (exact + fuzzy)

## API

- **`ocr_available()`** — `True` if pytesseract (and thus Tesseract) is available
- **`ocr_from_path(image_path)`** — Run plate OCR on a file path; returns `(text, error)`
- **`ocr_from_bytes(data)`** — Run plate OCR on image bytes (e.g. upload); returns `(text, error)`

Text is normalized to uppercase alphanumeric only (A–Z, 0–9). Config: `--psm 7` (single line), character whitelist.

## Dependencies

Optional. Install for vision tests and dashboard plate check:

- System: Tesseract (`tesseract-ocr` or `tesseract`)
- Python: `pip install -r requirements-vision.txt` (pytesseract, opencv-python, Pillow)

See **SETUP.md** and **docs/DOCUMENTATION_OVERVIEW.md**.
