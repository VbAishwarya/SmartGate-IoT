"""
License plate OCR using Tesseract.

Reads alphanumeric text from plate images (crops or full images containing a plate).
Uses --psm 7 (single line) and A-Z0-9 whitelist. Optional dependency: pytesseract, opencv-python, Pillow.
"""

import re
from pathlib import Path
from typing import Optional, Tuple

# Config for "single line" plate text
_TESS_CONFIG = r"--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def ocr_available() -> bool:
    """Return True if OCR dependencies (pytesseract) are available."""
    try:
        import pytesseract  # noqa: F401
        return True
    except ImportError:
        return False


def _run_ocr_on_image(img_array) -> Tuple[Optional[str], Optional[str]]:
    """
    Run Tesseract OCR on a grayscale or BGR image (numpy array).
    Returns (normalized_plate_text, error_message).
    """
    try:
        import cv2
        import pytesseract
        from PIL import Image
    except ImportError as e:
        return None, f"Import failed: {e}"

    if img_array is None or img_array.size == 0:
        return None, "Empty image"

    # Grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_array

    # Try Otsu threshold first (good for many plate images)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil_img = Image.fromarray(thresh)
    raw = pytesseract.image_to_string(pil_img, config=_TESS_CONFIG)
    text = "".join(raw.upper().split())
    text = re.sub(r"[^A-Z0-9]", "", text)

    if len(text) < 1:
        # Fallback: grayscale without threshold
        raw2 = pytesseract.image_to_string(Image.fromarray(gray), config=_TESS_CONFIG)
        text = "".join(raw2.upper().split())
        text = re.sub(r"[^A-Z0-9]", "", text)

    if len(text) < 1:
        return None, "OCR returned no characters"
    return text, None


def ocr_from_path(image_path) -> Tuple[Optional[str], Optional[str]]:
    """
    Run plate OCR on an image file.
    image_path: path-like or str to a JPEG/PNG file.
    Returns (normalized_plate_text, error_message). On success error_message is None.
    """
    try:
        import cv2
    except ImportError as e:
        return None, f"Import failed: {e}"

    path = Path(image_path)
    if not path.is_file():
        return None, f"File not found: {path}"
    img = cv2.imread(str(path))
    if img is None:
        return None, f"Could not read image: {path}"
    return _run_ocr_on_image(img)


def ocr_from_bytes(data: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Run plate OCR on image bytes (e.g. from an uploaded file).
    data: raw bytes of a JPEG/PNG image.
    Returns (normalized_plate_text, error_message). On success error_message is None.
    """
    try:
        import cv2
        import numpy as np
    except ImportError as e:
        return None, f"Import failed: {e}"

    if not data:
        return None, "Empty file"
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return None, "Unsupported or corrupt image"
    return _run_ocr_on_image(img)
