"""Unit tests for fuzzy logic (plate authorization with optical typo rules)."""

import pytest

from src.fuzzy_logic import check_plate_authorization


class TestFuzzyLogic:
    """Fuzzy plate matching (optical typo rules)."""

    def test_exact_match_authorized(self):
        authorized = ["ABC123", "XYZ789"]
        ok, match, score = check_plate_authorization("ABC123", authorized)
        assert ok is True
        assert match == "ABC123"
        assert score >= 0.85

    def test_optical_zero_vs_o_authorized(self):
        # 0 and O are in OPTICAL_MAP for '0' -> input "ABC12O" vs authorized "ABC120"
        ok, match, score = check_plate_authorization("ABC12O", ["ABC120"])
        assert ok is True
        assert match == "ABC120"

    def test_unauthorized_no_similar(self):
        authorized = ["ABC123", "XYZ789"]
        ok, match, score = check_plate_authorization("QQQ999", authorized)
        assert ok is False
        assert score < 0.85

    def test_first_three_case_insensitive(self):
        authorized = ["ABC123"]
        ok1, _, _ = check_plate_authorization("abc123", authorized)
        ok2, _, _ = check_plate_authorization("ABC123", authorized)
        assert ok1 is True and ok2 is True
