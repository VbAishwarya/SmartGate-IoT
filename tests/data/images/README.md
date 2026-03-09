# Sample images for vision/OCR tests

- **Format:** JPEG (`.jpg`/`.jpeg`) or PNG (`.png`).
- **Content:** License plate crops (for OCR) or full frames (for detection).
- **Naming:** e.g. `plate_authorized_01.jpg`, `plate_unauthorized_01.png`, `scene_approach_01.jpg`.
- **Resolution:** Prefer 640×480 or 1280×720 to match production.

Tests will skip if no files are present. Sample plates are available in **contrib/image_processing_ocr/number_plates/**; vision tests use them automatically.
