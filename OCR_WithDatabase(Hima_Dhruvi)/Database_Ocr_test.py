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

# ---------------- SETTINGS ----------------
OPEN_DISTANCE = 25
LOG_FILE = "gate_log2.txt"
IMAGE_FOLDER = "images"
DB_FILE = "plates.db"

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

# ---------------- DATABASE CHECK ----------------
def is_authorized(plate):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT plate FROM authorized_plates WHERE plate=?", (plate,))
    result = c.fetchone()
    conn.close()
    return result is not None

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
def preprocess_image(frame):
    img = Image.fromarray(frame)
    gray = ImageOps.grayscale(img)
    gray = ImageEnhance.Contrast(gray).enhance(4)
    gray = gray.resize((gray.size[0]*2, gray.size[1]*2))
    bw = gray.point(lambda x: 0 if x < 140 else 255, "1")
    return bw

def detect_text(image):
    config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw = pytesseract.image_to_string(image, config=config)

    text = raw.upper()
    text = "".join(text.split())
    text = re.sub(r"[^A-Z0-9]", "", text)

    if len(text) >= 5:
        return text
    return None

# ---------------- LOG ----------------
def log_entry(plate, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp},{plate},{status}\n")

# ---------------- MAIN ----------------
gate_open = False
last_plate = ""
plate_logged = False

print("Smart Gate Running (plates.db)...")

try:
    while True:

        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Always run OCR
        processed = preprocess_image(frame)
        plate = detect_text(processed)

        if plate and plate != last_plate:
            print("Detected:", plate)
            last_plate = plate
            plate_logged = False

        if plate and not plate_logged:

            if is_authorized(plate):
                print("AUTHORIZED")

                GREEN_LED.on()
                RED_LED.off()

                distance = round(sensor.distance * 100, 2)

                if distance <= OPEN_DISTANCE and not gate_open:
                    set_servo_open()
                    gate_open = True

                log_entry(plate, "AUTHORIZED")

            else:
                print("UNAUTHORIZED")

                GREEN_LED.off()
                RED_LED.on()
                log_entry(plate, "UNAUTHORIZED")

            plate_logged = True

        # Close gate when vehicle leaves
        distance = round(sensor.distance * 100, 2)
        if distance > OPEN_DISTANCE and gate_open:
            set_servo_close()
            gate_open = False
            GREEN_LED.off()
            RED_LED.on()

        # Show plate on screen
        cv2.putText(frame_bgr, f"Plate: {last_plate}",
                    (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 0), 3)

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
