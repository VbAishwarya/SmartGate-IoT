import RPi.GPIO as GPIO
import time

# ---------------- PINS ----------------
TRIG = 23
ECHO = 24

GREEN = 17
RED = 27

SERVO_PIN = 18

# -------------- SETTINGS --------------
OPEN_ANGLE = 90
CLOSE_ANGLE = 0
CAR_DISTANCE = 10  # cm

# -------------- SETUP -----------------
GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)

GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

GPIO.output(TRIG, False)
GPIO.output(GREEN, False)
GPIO.output(RED, True)   # Start with gate closed (RED ON)

time.sleep(2)

# -------- DISTANCE FUNCTION ----------
def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = (duration * 34300) / 2
    return distance

# -------- SERVO FUNCTION ----------
def set_angle(angle):
    duty = 2 + (angle / 18)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.4)
    servo.ChangeDutyCycle(0)

print("Smart Gate Running...")

gate_open = False

try:
    while True:
        distance = get_distance()
        print(f"Distance: {distance:.2f} cm")

        # OBJECT DETECTED
        if distance <= CAR_DISTANCE and not gate_open:
            print("Object Detected -> GREEN ON -> Gate OPEN")
            GPIO.output(GREEN, True)
            GPIO.output(RED, False)
            set_angle(OPEN_ANGLE)
            gate_open = True
            time.sleep(1)

        # NO OBJECT
        elif distance > CAR_DISTANCE and gate_open:
            print("No Object -> RED ON -> Gate CLOSED")
            GPIO.output(GREEN, False)
            GPIO.output(RED, True)
            set_angle(CLOSE_ANGLE)
            gate_open = False
            time.sleep(1)

        time.sleep(0.2)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    servo.stop()
    GPIO.cleanup()
