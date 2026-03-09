import difflib
from typing import List, Tuple, Optional

# Task 3: Confidence & Decision Logic - Fuzzy matching fallback (≥85%) (Jenish)

OPTICAL_MAP = {
    '1': ['I', 'L', 'l'], '2': ['Z', 'z'], '3': ['B'],
    '4': ['A'], '5': ['S', 's'], '6': ['b'],
    '7': ['T'], '8': ['B'], '9': ['g', 'q'], '0': ['O', 'o']
}


def check_plate_authorization(
    input_plate: str,
    authorized_plates: Optional[List[str]] = None,
    threshold: float = 0.85
) -> Tuple[bool, str, float]:
    """
    Check if a plate is authorized using fuzzy matching and optical typo rules.
    Returns (authorized, best_matched_plate, score).
    """
    if authorized_plates is None:
        authorized_plates = ["ABC123", "XYZ789", "DEF456"]
    best_match = ""
    highest_score = 0.0
    for auth_plate in authorized_plates:
        ratio_score = difflib.SequenceMatcher(None, input_plate.upper(), auth_plate.upper()).ratio()
        validation_points = 0
        for i in range(min(len(input_plate), len(auth_plate))):
            char_in = input_plate[i]
            char_auth = auth_plate[i]
            if i < 3:
                if char_in.upper() == char_auth.upper():
                    validation_points += 1
            else:
                if char_in == char_auth:
                    validation_points += 1
                elif char_auth in OPTICAL_MAP and char_in in OPTICAL_MAP[char_auth]:
                    validation_points += 0.95
                else:
                    validation_points += 0
        position_score = validation_points / len(auth_plate)
        final_score = (ratio_score + position_score) / 2
        if final_score > highest_score:
            highest_score = final_score
            best_match = auth_plate
    return (highest_score >= threshold, best_match, highest_score)


def check_authorization():
    threshold = 0.85
    authorized_plates = ["ABC123", "XYZ789", "DEF456"]
    print("--- SmartGate: Strict 85% Logic (with Approved Typos) ---")
    while True:
        input_plate = input("\nEnter plate: ").strip()
        if input_plate.lower() == 'exit':
            break
        authorized, best_match, score = check_plate_authorization(
            input_plate, authorized_plates, threshold
        )
        confidence = score * 100
        print(f"Match: {best_match} | Confidence: {confidence:.1f}%")
        if authorized:
            print("RESULT: [ AUTHORIZED ]")
        else:
            print("RESULT: [ REJECTED ]")
            print(f"Reason: Score below {int(threshold*100)}% (Unrecognized typo)")


if __name__ == "__main__":
    check_authorization()