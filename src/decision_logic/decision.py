from typing import List, Dict
from collections import Counter


def filter_confident_frames(
    frames: List[Dict[str, float]],
    confidence_threshold: float = 0.8
) -> List[Dict[str, float]]:
    """
    Filters frames based on OCR  .
    """
    return [frame for frame in frames if frame.get("confidence", 0) >= confidence_threshold]


def majority_voting(frames: List[Dict[str, float]]) -> Dict[str, str]:
    """
    Performs character-level frame-based majority voting.
    """
    valid_texts = [f["ocr_output"] for f in frames if f.get("ocr_output")]

    if not valid_texts:
        return {
            "decision": "ACCESS_DENIED",
            "ocr_text": None,
            "reason": "No valid OCR outputs after confidence filtering"
        }

    # Use most common text length to avoid misalignment
    length_counter = Counter(len(t) for t in valid_texts)
    target_length = length_counter.most_common(1)[0][0]

    aligned_texts = [t for t in valid_texts if len(t) == target_length]

    if not aligned_texts:
        return {
            "decision": "ACCESS_DENIED",
            "ocr_text": None,
            "reason": "No aligned OCR outputs for majority voting"
        }

    final_text = ""
    for i in range(target_length):
        chars_at_position = [text[i] for text in aligned_texts]
        final_text += Counter(chars_at_position).most_common(1)[0][0]

    return {
        "decision": "ACCESS_GRANTED",
        "ocr_text": final_text,
        "reason": f"Character-level majority voting using {len(aligned_texts)} frames"
    }


def execute_decision_logic(
    frames: List[Dict[str, float]],
    confidence_threshold: float = 0.8
) -> Dict[str, str]:
    """
    Executes confidence filtering followed by frame-based majority voting.
    """
    # Step 1: Confidence threshold filtering
    confident_frames = filter_confident_frames(frames, confidence_threshold)

    if not confident_frames:
        return {
            "decision": "ACCESS_DENIED",
            "ocr_text": None,
            "reason": f"All frames below confidence threshold {confidence_threshold}"
        }

    # Step 2: Frame-based majority voting
    return majority_voting(confident_frames)