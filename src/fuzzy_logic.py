import difflib

# Task 3: Confidence & Decision Logic - Fuzzy matching fallback (≥85%) (Jenish)

def check_authorization():
    authorized_plates = ["ABC123", "XYZ789", "DEF456"]
    
    # Higher threshold to block random error
    threshold = 0.85

    # Custom visual mapping
    optical_map = {
        '1': ['I', 'L', 'l'], '2': ['Z', 'z'], '3': ['B'],
        '4': ['A'], '5': ['S', 's'], '6': ['b'],
        '7': ['T'], '8': ['B'], '9': ['g', 'q'], '0': ['O', 'o']
    }

    print(f"--- SmartGate: Strict 85% Logic (with Approved Typos) ---")
    
    while True:
        input_plate = input("\nEnter plate: ").strip()
        if input_plate.lower() == 'exit': break

        best_match = ""
        highest_score = 0.0

        for auth_plate in authorized_plates:
            # 1. Similarity Ratio
            ratio_score = difflib.SequenceMatcher(None, input_plate.upper(), auth_plate.upper()).ratio()
            
            # 2. Strict Positional Validation
            validation_points = 0
            for i in range(min(len(input_plate), len(auth_plate))):
                char_in = input_plate[i]
                char_auth = auth_plate[i]

                # Rule 1: First 3 (Case-Insensitive)
                if i < 3:
                    if char_in.upper() == char_auth.upper():
                        validation_points += 1
                
                # Rule 2: Last 3 (Optical Approved Typos)
                else:
                    if char_in == char_auth:
                        validation_points += 1
                    # Give high credit ONLY if it is in approved map
                    elif char_auth in optical_map and char_in in optical_map[char_auth]:
                        validation_points += 0.95  # This keeps the score > 85%
                    else:
                        validation_points += 0 # Random character gets nothing
            
            position_score = validation_points / len(auth_plate)
            final_score = (ratio_score + position_score) / 2

            if final_score > highest_score:
                highest_score = final_score
                best_match = auth_plate

        confidence = highest_score * 100
        print(f"Match: {best_match} | Confidence: {confidence:.1f}%")

        if highest_score >= threshold:
            print("RESULT: [ AUTHORIZED ]")
        else:
            print("RESULT: [ REJECTED ]")
            print(f"Reason: Score below {int(threshold*100)}% (Unrecognized typo)")

if __name__ == "__main__":
    check_authorization()