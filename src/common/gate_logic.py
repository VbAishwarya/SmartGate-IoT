"""Gate decision logic shared between hardware (RPi) and tests.

This module stays pure (no GPIO/camera access) so it can be tested on any platform.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List, Optional, Literal


GateStatus = Literal["NO_PLATE", "AUTHORIZED_OPEN", "AUTHORIZED_FAR", "UNAUTHORIZED"]


@dataclass
class GateDecision:
    status: GateStatus
    plate: Optional[str]
    match: Optional[str]
    similarity: float


def decide_gate_action(
    plate_text: Optional[str],
    distance_cm: float,
    authorized_plates: List[str],
    open_distance_cm: float,
    fuzzy_threshold: float = 0.90,
) -> GateDecision:
    """
    Decide what the gate should do based on OCR plate text and distance.

    - plate_text: raw plate string from OCR (may be None/empty)
    - distance_cm: current distance from sensor
    - authorized_plates: list of known authorized plate strings
    - open_distance_cm: distance threshold at/below which gate may open
    - fuzzy_threshold: minimum similarity for fuzzy authorization (0..1)
    """
    normalized = (plate_text or "").strip().upper()
    if not normalized:
        return GateDecision(status="NO_PLATE", plate=None, match=None, similarity=0.0)

    best_match: Optional[str] = None
    best_ratio: float = 0.0

    for auth in authorized_plates:
        candidate = auth.strip().upper()
        if not candidate:
            continue
        ratio = SequenceMatcher(None, normalized, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate

    if best_match is not None and best_ratio >= fuzzy_threshold:
        if distance_cm <= open_distance_cm:
            status: GateStatus = "AUTHORIZED_OPEN"
        else:
            status = "AUTHORIZED_FAR"
        return GateDecision(
            status=status,
            plate=normalized,
            match=best_match,
            similarity=best_ratio,
        )

    return GateDecision(
        status="UNAUTHORIZED",
        plate=normalized,
        match=best_match,
        similarity=best_ratio,
    )

