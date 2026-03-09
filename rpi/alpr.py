import os
import re
import sqlite3
import time
from datetime import datetime

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps, ImageEnhance

from src.common.gate_logic import decide_gate_action


# ---------------- SETTINGS ----------------
LOG_FILE = "gate_log2.txt"
IMAGE_FOLDER = "images"
DB_FILE = "plates.db"
OPEN_DISTANCE = 50  # cm
FUZZY_THRESHOLD = 0.90  # 90% similarity

os.makedirs(IMAGE_FOLDER, exist_ok=True)


# Hardware resources are created inside main() so importing this module does
# not require a Raspberry Pi or camera/GPIO to be present.
GREEN_LED = None
RED_LED = None
sensor = None
servo = None
picam2 = None


# ---------------- DATABASE ----------------
def get_authorized_plates():
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("SELECT plate FROM authorized_plates")
        results = [row[0].upper() for row in c.fetchall()]
        return results
    finally:
        conn.close()


# ---------------- SERVO ----------------
def set_servo_open():
    if servo is None:
        return
    for i in np.linspace(-1, 0, 30):
        servo.value = i
        time.sleep(0.02)
    servo.detach()


def set_servo_close():
    if servo is None:
        return
    for i in np.linspace(0, -1, 30):
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
    Also saves intermediate images for documentation.
    """
    # Save original frame
    cv2.imwrite(os.path.join(IMAGE_FOLDER, "original_frame.jpg"), frame)

    pil_img = Image.fromarray(frame)

    # Grayscale
    gray = ImageOps.grayscale(pil_img)
    cv2.imwrite(os.path.join(IMAGE_FOLDER, "grayscale_image.jpg"), np.array(gray))

    # Contrast enhancement
    gray = ImageEnhance.Contrast(gray).enhance(4)

    # Resize
    gray = gray.resize((int(gray.size[0] * 1.3), int(gray.size[1] * 1.3)), Image.BILINEAR)

    # Threshold
    bw = gray.point(lambda x: 0 if x < 140 else 255, "1")

    # Save threshold image
    threshold_img = np.array(bw).astype(np.uint8) * 255
    cv2.imwrite(os.path.join(IMAGE_FOLDER, "threshold_image.jpg"), threshold_img)

    return bw


def detect_text(frame):
    plate_image = preprocess_plate(frame)

    # Save final processed OCR image
    processed_img = np.array(plate_image).astype(np.uint8) * 255
    cv2.imwrite(os.path.join(IMAGE_FOLDER, "processed_plate.jpg"), processed_img)

    config = r"--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw = pytesseract.image_to_string(plate_image, config=config)

    text = "".join(raw.upper().split())
    text = re.sub(r"[^A-Z0-9]", "", text)

    return text if len(text) >= 5 else None


# ---------------- LOG ----------------
def log_entry(plate, status, distance):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as file:
        file.write(f"{timestamp},{plate},{status},{distance}cm\n")


def main():
    global GREEN_LED, RED_LED, sensor, servo, picam2

    # Pi-only imports: required only when actually running on hardware
    try:
        from gpiozero import LED, DistanceSensor, Servo
        from picamera2 import Picamera2
        from libcamera import Transform
    except ModuleNotFoundError as e:
        print("This script must be run on a Raspberry Pi with hardware dependencies installed.")
        print("Install: pip install gpiozero picamera2; system: libcamera, opencv, tesseract")
        raise SystemExit(1) from e

    # ---------------- GPIO ----------------
    GREEN_LED = LED(17)
    RED_LED = LED(27)
    sensor = DistanceSensor(trigger=23, echo=24)

    servo = Servo(
        18,
        min_pulse_width=0.5 / 1000,   # 0 pulse
        max_pulse_width=2.5 / 1000,   # 180 pulse
        initial_value=None,
    )

    # ---------------- CAMERA ----------------
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (1280, 720), "format": "BGR888"},
        transform=Transform(hflip=1, vflip=1),
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)

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
                authorized_list = get_authorized_plates()
                decision = decide_gate_action(
                    plate_text=plate,
                    distance_cm=distance,
                    authorized_plates=authorized_list,
                    open_distance_cm=OPEN_DISTANCE,
                    fuzzy_threshold=FUZZY_THRESHOLD,
                )

                if decision.status in ("AUTHORIZED_OPEN", "AUTHORIZED_FAR"):
                    matched_plate = decision.match or plate
                    print(f"AUTHORIZED Plate: {matched_plate} (OCR: {plate}) | Distance: {distance} cm")
                    GREEN_LED.on()
                    RED_LED.off()

                    if decision.status == "AUTHORIZED_OPEN":
                        set_servo_open()
                        gate_open = True
                        open_time = time.time()

                        # Wait 5 seconds with gate open
                        while open_time is not None and (time.time() - open_time < 5):
                            cv2.putText(
                                frame_bgr,
                                f"Plate: {plate}",
                                (30, 60),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.2,
                                (0, 255, 0),
                                3,
                            )
                            cv2.putText(
                                frame_bgr,
                                f"Distance: {distance} cm",
                                (30, 110),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.0,
                                (0, 255, 255),
                                2,
                            )
                            cv2.imshow("Live Preview", frame_bgr)

                            if cv2.waitKey(1) & 0xFF == ord("q"):
                                raise KeyboardInterrupt

                            time.sleep(0.1)

                        set_servo_close()
                        gate_open = False
                        open_time = None
                        GREEN_LED.off()
                        RED_LED.on()
                        log_entry(matched_plate, "AUTHORIZED", distance)

                        print("Authorized vehicle processed. System stopped until manual restart.")
                        break  # stop OCR loop
                    else:
                        print("Authorized plate detected, but vehicle is outside gate opening distance.")

                else:
                    # ---------------- UNAUTHORIZED ----------------
                    print(f"UNAUTHORIZED Plate: {plate} | Distance: {distance} cm")
                    GREEN_LED.off()
                    RED_LED.on()
                    log_entry(plate, "UNAUTHORIZED", distance)

            # Auto-close gate if open
            if gate_open and open_time is not None:
                if time.time() - open_time >= 5:
                    set_servo_close()
                    gate_open = False
                    open_time = None
                    GREEN_LED.off()
                    RED_LED.on()

            # Live preview
            cv2.putText(
                frame_bgr,
                f"Plate: {last_plate}",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3,
            )
            cv2.putText(
                frame_bgr,
                f"Distance: {distance} cm",
                (30, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
            )
            cv2.imshow("Live Preview", frame_bgr)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        if servo is not None:
            servo.detach()
        if picam2 is not None:
            picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

