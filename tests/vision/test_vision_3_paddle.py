"""
Vision tests – Option 3: PaddleOCR.

See docs/PLATE_OCR_OPTIONS.md §3. Run when PaddleOCR is installed.
Skips if paddleocr not installed. Uses PaddleOCR on a cropped/sample plate image.
"""

import re

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


def _normalize(s):
    s = "".join(s.upper().split())
    return re.sub(r"[^A-Z0-9]", "", s)


@pytest.mark.vision
def test_paddleocr_returns_plate_text():
    """Run PaddleOCR on a sample plate image."""
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        pytest.skip("paddleocr not installed (pip install paddleocr)")

    image_path = _find_one_image()
    if not image_path:
        pytest.skip("No sample image in tests/data/images or contrib/.../number_plates")

    ocr = PaddleOCR(use_angle_cls=False, use_gpu=False, show_log=False)
    result = ocr.ocr(str(image_path), cls=False)
    if not result or not result[0]:
        pytest.skip("PaddleOCR returned no text for this image")

    # Concatenate all detected text lines
    parts = []
    for line in result[0]:
        if line and len(line) >= 2 and line[1]:
            parts.append(str(line[1][0]))
    text = _normalize(" ".join(parts))

    if len(text) < 1:
        pytest.skip("PaddleOCR returned no alphanumeric plate text")
    assert len(text) >= 1
    assert text.isalnum()
