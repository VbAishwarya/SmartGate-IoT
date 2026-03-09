import time
from gpiozero import LED, DistanceSensor, Servo
from picamera2 import Picamera2
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import re
import cv2
import numpy as np
from datetime import datetime
import os
import sqlite3
from difflib import SequenceMatcher

# ---------------- SETTINGS ----------------
LOG_FILE = "gate_log2.txt"
IMAGE_FOLDER = "images"
DB_FILE = "plates.db"
OPEN_DISTANCE = 25  # cm
FUZZY_THRESHOLD = 0.95  # 95% similarity

os.makedirs(IMAGE_FOLDER, exist_ok=True)


# ---------------- GPIO ----------------
GREEN_LED = LED(17)
RED_LED = LED(27)
sensor = DistanceSensor(trigger=23, echo=24)
servo = Servo(18, initial_value=None)

# ---------------- CAMERA ----------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (1280, 720)})
picam2.configure(config)
picam2.start()
time.sleep(2)

# ---------------- DATABASE ----------------
def get_authorized_plates():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT plate FROM authorized_plates")
    results = [row[0].upper() for row in c.fetchall()]
    conn.close()
    return results

def is_plate_authorized_fuzzy(plate):
    authorized_list = get_authorized_plates()
    for auth_plate in authorized_list:
        ratio = SequenceMatcher(None, plate, auth_plate).ratio()
        if ratio >= FUZZY_THRESHOLD:
            return True, auth_plate
    return False, None

# ---------------- SERVO ----------------
def set_servo_open():
    for i in np.linspace(-1, 1, 20):
        servo.value = i
        time.sleep(0.02)
    servo.detach()

def set_servo_close():
    for i in np.linspace(1, -1, 20):
        servo.value = i
        time.sleep(0.02)
    servo.detach()

# ---------------- OCR ----------------
def preprocess_plate(frame):
    """
    Improves OCR accuracy:
    - Grayscale
    - Upscale
    - Contrast enhancement
    - Thresholding to black letters on white
    """
    pil_img = Image.fromarray(frame)
    gray = ImageOps.grayscale(pil_img)
    gray = ImageEnhance.Contrast(gray).enhance(4)
    gray = gray.resize((gray.size[0]*2, gray.size[1]*2), Image.LANCZOS)
    bw = gray.point(lambda x: 0 if x < 140 else 255, "1")
    return bw

def detect_text(frame):
    plate_image = preprocess_plate(frame)
    config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw = pytesseract.image_to_string(plate_image, config=config)
    text = "".join(raw.upper().split())
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text if len(text) >= 5 else None

# ---------------- LOG ----------------
def log_entry(plate, status, distance):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp},{plate},{status},{distance}cm\n")

# ---------------- MAIN LOOP ----------------
gate_open = False
open_time = None
last_plate = ""

print("Smart Gate Running...")

try:
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Distance measurement
        distance = round(sensor.distance * 100, 2)

        # OCR detection
        plate = detect_text(frame_bgr)

        if plate and plate != last_plate:
            last_plate = plate
            authorized, matched_plate = is_plate_authorized_fuzzy(plate)

            if authorized:
                # ---------------- AUTHORIZED ----------------
                print(f"AUTHORIZED Plate: {matched_plate} (OCR: {plate}) | Distance: {distance} cm")
                GREEN_LED.on()
                RED_LED.off()

                if distance <= OPEN_DISTANCE:
                    set_servo_open()
                    gate_open = True
                    open_time = time.time()

                # Wait 5 seconds with gate open
                while time.time() - open_time < 5:
                    cv2.putText(frame_bgr, f"Plate: {plate}", (30, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                    cv2.putText(frame_bgr, f"Distance: {distance} cm", (30, 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                    cv2.imshow("Live Preview", frame_bgr)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        raise KeyboardInterrupt
                    time.sleep(0.1)

                set_servo_close()
                GREEN_LED.off()
                RED_LED.on()
                log_entry(matched_plate, "AUTHORIZED", distance)

                print("Authorized vehicle processed. System stopped until manual restart.")
                break  # stop OCR

            else:
                # ---------------- UNAUTHORIZED ----------------
                print(f"UNAUTHORIZED Plate: {plate} | Distance: {distance} cm")
                GREEN_LED.off()
                RED_LED.on()
                log_entry(plate, "UNAUTHORIZED", distance)
                # OCR continues

        # Auto-close gate if open
        if gate_open and open_time:
            if time.time() - open_time >= 5:
                set_servo_close()
                gate_open = False
                open_time = None
                GREEN_LED.off()
                RED_LED.on()

        # Live preview
        cv2.putText(frame_bgr, f"Plate: {last_plate}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(frame_bgr, f"Distance: {distance} cm", (30, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.imshow("Live Preview", frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    servo.detach()
    picam2.stop()
    cv2.destroyAllWindows()
