"""Unit tests for gate decision logic used by Raspberry Pi ALPR."""

from src.common.gate_logic import decide_gate_action


def test_no_plate_returns_no_plate_status():
    decision = decide_gate_action(
        plate_text=None,
        distance_cm=40.0,
        authorized_plates=["ABC123"],
        open_distance_cm=50.0,
    )
    assert decision.status == "NO_PLATE"
    assert decision.plate is None
    assert decision.match is None
    assert decision.similarity == 0.0


def test_exact_match_within_distance_opens_gate():
    decision = decide_gate_action(
        plate_text="abc123",
        distance_cm=30.0,
        authorized_plates=["ABC123"],
        open_distance_cm=50.0,
    )
    assert decision.status == "AUTHORIZED_OPEN"
    assert decision.plate == "ABC123"
    assert decision.match == "ABC123"
    assert decision.similarity == 1.0


def test_exact_match_outside_distance_does_not_open_gate():
    decision = decide_gate_action(
        plate_text="ABC123",
        distance_cm=60.0,
        authorized_plates=["ABC123"],
        open_distance_cm=50.0,
    )
    assert decision.status == "AUTHORIZED_FAR"
    assert decision.match == "ABC123"


def test_fuzzy_match_above_threshold_treated_as_authorized():
    # ABC12 is very similar to ABC123; with threshold 0.8 it should be accepted.
    decision = decide_gate_action(
        plate_text="ABC12",
        distance_cm=40.0,
        authorized_plates=["ABC123"],
        open_distance_cm=50.0,
        fuzzy_threshold=0.80,
    )
    assert decision.status == "AUTHORIZED_OPEN"
    assert decision.match == "ABC123"
    assert 0.80 <= decision.similarity <= 1.0


def test_fuzzy_match_below_threshold_is_unauthorized():
    decision = decide_gate_action(
        plate_text="ABC12",
        distance_cm=40.0,
        authorized_plates=["ABC123"],
        open_distance_cm=50.0,
        fuzzy_threshold=0.99,
    )
    assert decision.status == "UNAUTHORIZED"
    # best_match may still be ABC123, but similarity is below the stricter threshold
    assert decision.match in (None, "ABC123")
    assert decision.similarity < 0.99


def test_completely_different_plate_is_unauthorized():
    decision = decide_gate_action(
        plate_text="ZZZ999",
        distance_cm=20.0,
        authorized_plates=["ABC123", "XYZ789"],
        open_distance_cm=50.0,
    )
    assert decision.status == "UNAUTHORIZED"
    assert decision.plate == "ZZZ999"

