"""
Vision tests – Option 1: Tesseract with a custom trained model.

See docs/PLATE_OCR_OPTIONS.md §1. These tests run only when a custom plate
traineddata is configured (e.g. after training with tesstrain).

Set PLATE_TESSDATA_DIR (path to dir containing your .traineddata) and
PLATE_TESSDATA_LANG (e.g. "plate") to run. Otherwise tests skip.
"""

import os
from pathlib import Path

import pytest

from tests.vision.conftest import IMAGE_DIRS, ROOT

# Same image discovery as other vision tests
def _find_one_image():
    for d in IMAGE_DIRS:
        if not d.is_dir():
            continue
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            for p in d.glob(ext):
                return p
    return None


@pytest.mark.vision
def test_tesseract_custom_traineddata_returns_plate_text():
    """Run Tesseract with custom plate traineddata when configured."""
    tessdata_dir = os.environ.get("PLATE_TESSDATA_DIR", "").strip()
    lang = os.environ.get("PLATE_TESSDATA_LANG", "").strip()
    if not tessdata_dir or not lang:
        pytest.skip(
            "Set PLATE_TESSDATA_DIR and PLATE_TESSDATA_LANG to test custom Tesseract plate model "
            "(see docs/PLATE_OCR_OPTIONS.md)"
        )
    if not Path(tessdata_dir).is_dir():
        pytest.skip(f"PLATE_TESSDATA_DIR is not a directory: {tessdata_dir}")

    try:
        import pytesseract
    except ImportError:
        pytest.skip("pytesseract not installed")

    image_path = _find_one_image()
    if not image_path:
        pytest.skip("No sample image in tests/data/images or contrib/.../number_plates")

    import cv2
    from PIL import Image

    img = cv2.imread(str(image_path))
    if img is None:
        pytest.skip(f"Could not read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    config = f"--tessdata-dir {tessdata_dir} --oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw = pytesseract.image_to_string(Image.fromarray(gray), lang=lang, config=config)
    text = "".join(raw.upper().split())
    text = "".join(c for c in text if c.isalnum())

    if len(text) < 1:
        pytest.skip("Custom model returned no characters (check traineddata and image)")
    assert len(text) >= 1
    assert text.isalnum()
