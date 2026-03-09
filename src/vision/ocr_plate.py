"""
License plate OCR using Tesseract, with optional EasyOCR backend.

Reads alphanumeric text from plate images (crops or full images containing a plate).
Supports Indian, European (EU strip, hyphens, stickers) by cropping the EU strip,
using high-confidence word-level data to skip noise, and allowing hyphens in raw output.

Set SMARTGATE_OCR_BACKEND=easyocr to use EasyOCR when installed (often better for EU plates).
See docs/PLATE_OCR_OPTIONS.md for other model options.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

# PSM 7 = single line, 8 = single word, 6 = block (helps EU plates with spaces/stickers)
_PSM_MODES = [7, 8, 6]
# Whitelist including hyphen so "WD-71817" / "KI-EL 1" read correctly; we strip hyphen when normalizing
_TESS_WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"


def _normalize(raw: str) -> str:
    """Extract A-Z0-9 only, uppercase; collapse spaces and remove hyphens."""
    s = "".join(raw.upper().split()).replace("-", "")
    return re.sub(r"[^A-Z0-9]", "", s)


def ocr_available() -> bool:
    """Return True if an OCR backend is available (pytesseract or EasyOCR when env set)."""
    if os.environ.get("SMARTGATE_OCR_BACKEND", "").strip().lower() == "easyocr":
        try:
            import easyocr  # noqa: F401
            return True
        except ImportError:
            pass
    try:
        import pytesseract  # noqa: F401
        return True
    except ImportError:
        return False


def _run_ocr_on_image(img_array) -> Tuple[Optional[str], Optional[str]]:
    """
    Run OCR; uses EasyOCR if SMARTGATE_OCR_BACKEND=easyocr and EasyOCR is installed,
    otherwise Tesseract (optimized for European plates).
    """
    try:
        import cv2
    except ImportError as e:
        return None, f"Import failed: {e}"

    if img_array is None or img_array.size == 0:
        return None, "Empty image"

    # Optional EasyOCR backend (often better for EU plates / odd fonts)
    if os.environ.get("SMARTGATE_OCR_BACKEND", "").strip().lower() == "easyocr":
        try:
            import easyocr
            import numpy as np
            if getattr(_run_ocr_on_image, "_easyocr_reader", None) is None:
                _run_ocr_on_image._easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            reader = _run_ocr_on_image._easyocr_reader
            if len(img_array.shape) == 2:
                img = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
            else:
                img = np.asarray(img_array)
            results = reader.readtext(img)
            for _bbox, text, _conf in results:
                norm = _normalize(str(text))
                if len(norm) >= 4:
                    return norm, None
            if results:
                norm = _normalize(" ".join(str(r[1]) for r in results))
                if len(norm) >= 4:
                    return norm, None
        except ImportError:
            pass
        except Exception as e:
            return None, f"EasyOCR error: {e}"

    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        return None, f"Import failed: {e}"

    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_array

    h, w = gray.shape[:2]
    if max(h, w) < 200:
        scale = 200 / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        h, w = gray.shape[:2]

    def make_crop(left_pct: float, right_pct: float = 0.05):
        x0 = int(w * left_pct)
        x1 = int(w * (1 - right_pct))
        return gray[:, x0:x1] if x1 - x0 > 80 else gray

    # EU strip ~12–20% left; try moderate and aggressive crop so we don't cut into "KI" / "B" etc.
    gray_eu_25 = make_crop(0.25)
    gray_eu_35 = make_crop(0.35)

    def run_tesseract(im, psm: int, whitelist: str = _TESS_WHITELIST) -> str:
        cfg = f"--oem 3 --psm {psm} -c tessedit_char_whitelist={whitelist}"
        raw = pytesseract.image_to_string(im, config=cfg)
        return _normalize(raw)

    def run_tesseract_data(im, psm: int) -> str:
        """High-confidence words only (drops blue strip / sticker noise)."""
        cfg = f"--oem 3 --psm {psm} -c tessedit_char_whitelist={_TESS_WHITELIST}"
        try:
            data = pytesseract.image_to_data(im, config=cfg, output_type=pytesseract.Output.DICT)
        except Exception:
            return ""
        parts = []
        for i, conf in enumerate(data.get("conf", [])):
            if conf is None:
                continue
            try:
                c = int(conf)
            except (TypeError, ValueError):
                continue
            if c < 50:
                continue
            text = (data.get("text") or [])
            if i < len(text) and text[i]:
                t = str(text[i]).strip()
                if t and t != "-":
                    parts.append(t)
        return _normalize(" ".join(parts))

    def add_candidates(im_pil, label: str) -> None:
        for psm in _PSM_MODES:
            t = run_tesseract(im_pil, psm)
            if len(t) >= 4:
                candidates.append((t, label))
        for psm in [6, 7]:
            t = run_tesseract_data(im_pil, psm)
            if len(t) >= 4:
                candidates.append((t, "data"))

    candidates: List[Tuple[str, str]] = []

    # 1) Full image – Otsu
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    add_candidates(Image.fromarray(thresh), "full_otsu")

    # 2) Full image – grayscale
    add_candidates(Image.fromarray(gray), "full_gray")

    # 3) EU crop 25% left – Otsu, grayscale, adaptive
    _, thresh_25 = cv2.threshold(gray_eu_25, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    add_candidates(Image.fromarray(thresh_25), "eu25_otsu")
    add_candidates(Image.fromarray(gray_eu_25), "eu25_gray")
    try:
        adapt_25 = cv2.adaptiveThreshold(
            gray_eu_25, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        add_candidates(Image.fromarray(adapt_25), "eu25_adapt")
    except Exception:
        pass

    # 4) EU crop 35% left (aggressive – strip only)
    _, thresh_35 = cv2.threshold(gray_eu_35, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    add_candidates(Image.fromarray(thresh_35), "eu35_otsu")
    add_candidates(Image.fromarray(gray_eu_35), "eu35_gray")

    if not candidates:
        return None, "OCR returned no characters (try a clearer plate image or check Tesseract)"

    # Prefer result that looks like a plate: 5–11 chars, mix of letters and digits; prefer data path
    def score(s: str, label: str) -> Tuple[float, int]:
        data_bonus = 2.0 if label == "data" else 0.0
        length_ok = 1.0 if 5 <= len(s) <= 11 else (0.5 if 4 <= len(s) <= 12 else 0)
        has_alpha = 0.5 if any(c.isalpha() for c in s) else 0
        has_digit = 0.5 if any(c.isdigit() for c in s) else 0
        # Slight penalty for leading "B" (often EU strip misread) when "E" + rest would be a valid plate
        strip_b_penalty = 0.0
        if len(s) >= 3 and s.startswith("BE") and s[2:].isalnum():
            strip_b_penalty = 0.3
        return (data_bonus + length_ok + has_alpha + has_digit - strip_b_penalty, len(s))

    # If we have "BE..." and "EU..." of same length, prefer "EU..." (EU strip artifact)
    texts = [c[0] for c in candidates]
    def strip_leading_b(s: str) -> str:
        if len(s) >= 3 and s.startswith("BE") and s[2:].isalnum():
            return s[1:]
        return s
    best = max(candidates, key=lambda x: score(x[0], x[1]))
    best_text = best[0]
    without_b = strip_leading_b(best_text)
    # If best is "BE..." (EU strip artifact), prefer "E..." when it looks like a plate
    if best_text.startswith("BE") and len(best_text) >= 6 and best_text[1:2] == "E":
        candidate = best_text[1:]
        if any(c.isdigit() for c in candidate) and any(c.isalpha() for c in candidate):
            best_text = candidate
    elif without_b != best_text and without_b in texts and 5 <= len(without_b) <= 11:
        best_text = without_b
    return best_text, None


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
