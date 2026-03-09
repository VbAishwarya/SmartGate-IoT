# Test data and fixtures

- **Pytest fixtures** (e.g. temp DB, mock sensor): defined in `tests/conftest.py`.
- **Static fixtures** (images, videos): optional; used by vision/integration tests.

## Directories

| Directory    | Purpose | Format |
|-------------|--------|--------|
| `images/`   | Static images for OCR/detection tests | JPEG, PNG (see `images/README.md`) |
| `videos/`   | Short clips for scenario/detection tests | MP4 (see `videos/README.md`) |

If `images/` or `videos/` are missing, vision tests that depend on them will skip. Sample plate images are in **contrib/image_processing_ocr/number_plates/**; vision tests look there automatically.
