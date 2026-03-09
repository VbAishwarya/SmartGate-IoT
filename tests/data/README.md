# tests/data — Test data and fixtures

This directory holds **static test assets** (images and videos) used by vision and integration tests. It is separate from **pytest fixtures** (e.g. temporary DB, mock sensor), which are defined in `tests/conftest.py`.

## What goes here

| Directory   | Purpose | Format |
|------------|--------|--------|
| **images/**  | Plate crops or full-frame images for OCR/detection tests | JPEG, PNG. Prefer 640×480 or 1280×720. Example names: `plate_authorized_01.jpg`, `scene_approach_01.jpg`. |
| **videos/**  | Short clips for scenario or detection tests | MP4 (e.g. H.264). 5–15 s. Example names: `scenario_quick_pass.mp4`, `scenario_slow_approach.mp4`. |

You can leave **images/** and **videos/** empty. Vision tests also look in **contrib/image_processing_ocr/number_plates/** for sample plate images, so they run without adding files here. If a test needs a file from this tree and it’s missing, that test is skipped.

## Summary

- **tests/data** = optional static files (images, videos) for tests.
- **tests/conftest.py** = in-memory/temp fixtures (DB, sensor, paths) used by all tests.

See [docs/TESTING.md](../docs/TESTING.md) for how to run vision tests and add media.
