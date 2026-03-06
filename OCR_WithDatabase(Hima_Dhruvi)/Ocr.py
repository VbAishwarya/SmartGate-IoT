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

# ----------------------- GPIO PINS -----------------------
GREEN_LED_PIN = 17
RED_LED_PIN = 27
SERVO_PIN = 18
TRIG_PIN = 23
ECHO_PIN = 24
# ----------------------- SETTINGS -----------------------
OBJECT_DISTANCE = 10  # cm
LOG_FILE = "gate_log2.txt"
IMAGE_FOLDER = "images"
DATABASE_FILE = "authorized_plates.txt"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# ----------------------- GPIO SETUP ----------------------
GREEN_LED = LED(GREEN_LED_PIN)
RED_LED = LED(RED_LED_PIN)
sensor = DistanceSensor(trigger=TRIG_PIN, echo=ECHO_PIN)
servo = Servo(SERVO_PIN, initial_value=None)

# ----------------------- CAMERA SETUP --------------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)


# ----------------------- DATABASE LOAD -------------------
def load_authorized_plates():
    if not os.path.exists(DATABASE_FILE):
        print("Database file not found!")
        return set()
    with open(DATABASE_FILE, "r") as file:
        plates = {line.strip().upper() for line in file}
    return plates


AUTHORIZED_PLATES = load_authorized_plates()


# ----------------------- SERVO CONTROL -------------------
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


# ----------------------- IMAGE PROCESS -------------------
def preprocess_image(frame_array):
    img = Image.fromarray(frame_array)
    gray = ImageOps.grayscale(img)
    gray = ImageEnhance.Contrast(gray).enhance(3.5)
    gray = gray.resize((gray.size[0] * 2, gray.size[1] * 2))
    bw = gray.point(lambda x: 0 if x < 130 else 255, "1")
    return bw


def detect_text(image):
    config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    text = pytesseract.image_to_string(image, config=config)
    text = text.upper()
    text = "".join(text.split())
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


# ----------------------- LOG FUNCTION --------------------
def log_entry(plate_text, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp},{plate_text},{status}\n")


# ----------------------- MAIN LOOP -----------------------
gate_open = False
plate_checked = False

try:
    while True:
        distance = round(sensor.distance * 100, 2)
        print(f"Distance: {distance:.2f} cm")

        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if distance <= OBJECT_DISTANCE:

            if not plate_checked:
                processed = preprocess_image(frame)
                detected_plate = detect_text(processed)

                if detected_plate:
                    print("Detected Plate:", detected_plate)

                    if detected_plate in AUTHORIZED_PLATES:
                        print("Authorized Vehicle ?")

                        GREEN_LED.on()
                        RED_LED.off()

                        set_servo_open()
                        gate_open = True

                        log_entry(detected_plate, "AUTHORIZED")

                    else:
                        print("Unauthorized Vehicle ?")

                        GREEN_LED.off()
                        RED_LED.on()

                        set_servo_close()
                        gate_open = False

                        log_entry(detected_plate, "UNAUTHORIZED")

                    plate_checked = True

                else:
                    print("No plate detected")

        else:
            GREEN_LED.off()
            RED_LED.on()

            if gate_open:
                set_servo_close()
                gate_open = False

            plate_checked = False

        cv2.imshow("Live Preview", frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.3)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    servo.detach()
    picam2.stop()
    cv2.destroyAllWindows()
