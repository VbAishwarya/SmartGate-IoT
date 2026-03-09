"""
Shared fixtures for vision/OCR tests (one per PLATE_OCR_OPTIONS backend).

See docs/PLATE_OCR_OPTIONS.md for the four options. Image paths are taken from
tests/data/images/ and contrib/image_processing_ocr/number_plates/.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_DIRS = [
    ROOT / "tests" / "data" / "images",
    ROOT / "contrib" / "image_processing_ocr" / "number_plates",
]


def _collect_vision_images():
    out = []
    for dir_path in IMAGE_DIRS:
        if not dir_path.is_dir():
            continue
        for ext in ("*.jpg", "*.jpeg", "*.png"):
            out.extend(dir_path.glob(ext))
    return sorted(out)


@pytest.fixture(scope="module")
def vision_image_paths():
    """List of paths to sample plate images (empty if none found)."""
    return _collect_vision_images()


@pytest.fixture(scope="module")
def one_vision_image(vision_image_paths):
    """Single sample image path or None."""
    return vision_image_paths[0] if vision_image_paths else None
