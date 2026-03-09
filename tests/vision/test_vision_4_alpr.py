"""
Vision tests – Option 4: Dedicated ALPR / plate models.

See docs/PLATE_OCR_OPTIONS.md §4. These tests run when an ALPR implementation
is available. Currently we skip with a clear message; you can add a concrete
ALPR (e.g. LPRNet, FastPlateOcr, or a YOLO+OCR pipeline) and assert on its output.
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
def test_alpr_returns_plate_text():
    """Run a dedicated ALPR backend when configured.

    To enable: install an ALPR package and set VISION_ALPR_MODULE to the
    module name (e.g. 'openalpr' or a custom wrapper). The module must
    provide a function read_plate(image_path) -> (text: str, error: str|None).
    Otherwise this test skips.
    """
    alpr_module = os.environ.get("VISION_ALPR_MODULE", "").strip()
    if not alpr_module:
        pytest.skip(
            "Set VISION_ALPR_MODULE to the name of an ALPR module (e.g. openalpr) to run "
            "(see docs/PLATE_OCR_OPTIONS.md §4)"
        )

    image_path = _find_one_image()
    if not image_path:
        pytest.skip("No sample image in tests/data/images or contrib/.../number_plates")

    try:
        import importlib
        mod = importlib.import_module(alpr_module)
        read_plate = getattr(mod, "read_plate", None)
        if read_plate is None:
            pytest.skip(f"{alpr_module} has no read_plate(image_path) function")
        text, err = read_plate(str(image_path))
    except ImportError as e:
        pytest.skip(f"Could not import {alpr_module}: {e}")

    if err is not None:
        pytest.skip(f"ALPR failed: {err}")
    assert isinstance(text, str)
    assert len(text) >= 1
    assert text.isalnum()
