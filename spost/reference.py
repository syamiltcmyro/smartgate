import RPi.GPIO as GPIO
import time
import cv2
import pytesseract
from subprocess import Popen, PIPE

# GPIO setup for Ultrasonic Sensor and Relay
GPIO.setmode(GPIO.BCM)
TRIG_PIN1 = 23  # Trigger pin for ultrasonic sensor
ECHO_PIN1 = 24  # Echo pin for ultrasonic sensor
TRIG_PIN2 = 17  # Trigger pin for ultrasonic sensor
ECHO_PIN2 = 27  # Echo pin for ultrasonic sensor
LOCK_PIN = 18  # GPIO pin to control the door lock relay
GPIO.setup(TRIG_PIN1, GPIO.OUT)
GPIO.setup(ECHO_PIN1, GPIO.IN)
GPIO.setup(TRIG_PIN2, GPIO.OUT)
GPIO.setup(ECHO_PIN2, GPIO.IN)
GPIO.setup(LOCK_PIN, GPIO.OUT)



def measure_distance1():
    # Send a pulse to the trigger pin
    GPIO.output(TRIG_PIN1, True)
    time.sleep(0.00001)  # Send for 10 microseconds
    GPIO.output(TRIG_PIN1, False)

    # Wait for the echo pin to go HIGH and LOW, measuring the duration
    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO_PIN1) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN1) == 1:
        stop_time = time.time()

    # Calculate the time difference and convert to distance
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2  # Speed of sound is 34300 cm/s
    return distance

def measure_distance2():
    # Send a pulse to the trigger pin
    GPIO.output(TRIG_PIN2, True)
    time.sleep(0.00001)  # Send for 10 microseconds
    GPIO.output(TRIG_PIN2, False)

    # Wait for the echo pin to go HIGH and LOW, measuring the duration
    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO_PIN2) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN2) == 1:
        stop_time = time.time()

    # Calculate the time difference and convert to distance
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2  # Speed of sound is 34300 cm/s
    return distance

def capture_image1():
    # Capture the image using the camera
    process = Popen(["libcamera-still", "--camera", "0", "--width", "640", "--height", "480", "--timeout", "5000", "-o", "captured.jpg"], stdout=PIPE)
    process.wait()

def capture_image2():
    # Capture the image using the camera
    process = Popen(["libcamera-still", "--camera", "1", "--width", "640", "--height", "480", "--timeout", "5000", "-o", "captured.jpg"], stdout=PIPE)
    process.wait()

def perform_ocr(image_path):
    # Load the captured image and convert it from BGR to RGB
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Use Tesseract to OCR the image
    text = pytesseract.image_to_string(image)
    print("Detected Text:", text)
    
    # Save the detected text to a2.txt
    with open("a2.txt", "a") as text_file:
        text_file.write(text)
        text_file.write("\n")

    return text.strip()

def check_for_match(new_text, reference_file):
    # Read the content of a1.txt
    with open(reference_file, "r") as ref_file:
        ref_content = ref_file.read()
        print("License plate: ", new_text)
    
    # Check if the new text exists in a1.txt
    if new_text == "":
        print("Nothing detected")
    
    elif new_text in ref_content:
        print("Match found! Triggering door lock.")
        GPIO.output(LOCK_PIN, GPIO.LOW)  # Deactivate the relay (unlock the door)
        print("Door Unlocked")
    else:
        print("No match found.")

# def trigger_door_lock(distance):
#     if distance <= 5:
#         GPIO.output(LOCK_PIN, GPIO.HIGH)  # Activate the relay (lock the door)
#         print("Door Locked")
#     else:
#         GPIO.output(LOCK_PIN, GPIO.LOW)  # Deactivate the relay (unlock the door)
#         print("Door Unlocked")