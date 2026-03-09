"""Vision/OCR utilities for license plate reading."""

from .ocr_plate import ocr_from_path, ocr_from_bytes, ocr_available

__all__ = ["ocr_from_path", "ocr_from_bytes", "ocr_available"]
