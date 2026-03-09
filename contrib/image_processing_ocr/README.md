# Image Processing & OCR

This folder is **contrib** (hardware/experimental) content. In the project’s docs it’s referred to as **contrib/image_processing_ocr**.

## Contents

- **Image Processing & OCR Module.ipynb** — Jupyter notebook for plate OCR (Tesseract, preprocessing). Designed for Google Colab (uses `google.colab` for drive mount and file upload).
- **number_plates/** — Sample plate images (PNG/JPEG) for testing OCR.

## Relation to main app

- The **main application** (`main.py`) uses a **mock sensor** and does not run camera/OCR; it’s hardware-free.
- OCR and image processing for **real hardware** live here and in `contrib/ocr_with_database/`.
- Vision tests under `tests/vision/` use images from **number_plates/** when available (see `docs/TESTING.md`).

## Running the notebook

- In **Colab**: upload the notebook and run (Tesseract is installed in a cell).
- **Locally**: install `pytesseract` and system Tesseract; replace Colab-specific cells (e.g. `drive.mount`, `files.upload`) with local paths.

## Naming

This directory is **contrib/image_processing_ocr**. See `contrib/README.md` and `docs/ARCHITECTURE.md` for conventions.
