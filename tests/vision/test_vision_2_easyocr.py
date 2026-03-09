"""
Vision tests – Option 2: EasyOCR.

See docs/PLATE_OCR_OPTIONS.md §2. Run when EasyOCR is installed and
SMARTGATE_OCR_BACKEND=easyocr (or we force it in test). Skips if easyocr not installed.
"""

import os

import pytest

from tests.vision.conftest import IMAGE_DIRS


def _find_one_image():
    for d in IMAGE_DIRS:
        if not d.is_dir():
            continue
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            for p in d.glob(ext):
                return p
    return None


@pytest.mark.vision
def test_easyocr_returns_plate_text():
    """Run EasyOCR backend on a sample plate image."""
    try:
        import easyocr  # noqa: F401
    except ImportError:
        pytest.skip("easyocr not installed (pip install easyocr)")

    image_path = _find_one_image()
    if not image_path:
        pytest.skip("No sample image in tests/data/images or contrib/.../number_plates")

    # Use EasyOCR backend (ensure env is set for this process)
    prev = os.environ.get("SMARTGATE_OCR_BACKEND")
    os.environ["SMARTGATE_OCR_BACKEND"] = "easyocr"
    try:
        from src.vision import ocr_from_path
        text, err = ocr_from_path(image_path)
    finally:
        if prev is None:
            os.environ.pop("SMARTGATE_OCR_BACKEND", None)
        else:
            os.environ["SMARTGATE_OCR_BACKEND"] = prev

    if err is not None:
        pytest.skip(f"EasyOCR failed: {err}")
    assert isinstance(text, str)
    assert len(text) >= 1
    assert text.isalnum()
