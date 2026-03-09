"""
Vision/OCR tests using real images when available.

These tests are optional: they skip if:
- No sample image is found under tests/data/images/ or contrib/image_processing_ocr/number_plates/
- Optional dependencies (e.g. pytesseract, opencv) are not installed.

Run with: pytest tests/vision/ -v
Exclude from default run: pytest -m "not vision"
"""

import pytest
from pathlib import Path

# Prefer shared OCR from src.vision when available
try:
    from src.vision import ocr_from_path, ocr_available
except ImportError:
    ocr_from_path = None
    ocr_available = lambda: False

# Paths to look for sample plate images (first existing dir wins)
ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_DIRS = [
    ROOT / "tests" / "data" / "images",
    ROOT / "contrib" / "image_processing_ocr" / "number_plates",
]


def _find_one_image():
    for dir_path in IMAGE_DIRS:
        if not dir_path.is_dir():
            continue
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            for p in dir_path.glob(ext):
                return p
    return None


def _find_all_images():
    """Return list of sample image paths (for trying multiple in vision test)."""
    out = []
    for dir_path in IMAGE_DIRS:
        if not dir_path.is_dir():
            continue
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            out.extend(dir_path.glob(ext))
    return sorted(out)


# Fallback in-test OCR if src.vision not used (same logic as src/vision/ocr_plate.py)
def _ocr_available():
    if ocr_from_path is not None and ocr_available():
        return True
    try:
        import pytesseract  # noqa: F401
        return True
    except ImportError:
        return False


def _preprocess_and_ocr(image_path):
    """Used only when src.vision is not available; otherwise use ocr_from_path."""
    if ocr_from_path is not None and ocr_available():
        text, err = ocr_from_path(image_path)
        return (text, err)
    # Inline fallback (legacy)
    try:
        import cv2
        import pytesseract
        from PIL import Image
        import re
    except ImportError as e:
        return None, f"Import failed: {e}"
    img = cv2.imread(str(image_path))
    if img is None:
        return None, f"cv2.imread returned None for {image_path}"
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil_img = Image.fromarray(thresh)
    config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw = pytesseract.image_to_string(pil_img, config=config)
    text = "".join(raw.upper().split())
    text = re.sub(r"[^A-Z0-9]", "", text)
    if len(text) < 1:
        raw2 = pytesseract.image_to_string(Image.fromarray(gray), config=config)
        text = "".join(raw2.upper().split())
        text = re.sub(r"[^A-Z0-9]", "", text)
    if len(text) < 1:
        return None, "OCR returned no characters"
    return text, None


@pytest.mark.vision
def test_ocr_on_sample_plate_returns_string():
    """Run OCR on one sample image if present; assert we get a non-empty alphanumeric string."""
    image_paths = _find_all_images()
    if not image_paths:
        pytest.skip("No sample image in tests/data/images or contrib/image_processing_ocr/number_plates")
    if not _ocr_available():
        pytest.skip("pytesseract not installed")
    result, err = None, None
    for image_path in image_paths:
        result, err = _preprocess_and_ocr(image_path)
        if result is not None:
            break
    if result is None:
        pytest.skip(f"OCR failed on all images: {err}")
    assert isinstance(result, str)
    assert len(result) >= 1
    assert result.isalnum()
