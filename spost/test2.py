import RPi.GPIO as GPIO
import time
import cv2
import pytesseract
import numpy as np
from subprocess import Popen, PIPE
import xmlrpc.client

# Setup for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Odoo Connection Details
ODOO_HOST = 'your_odoo_host'            # Replace with your Odoo host
ODOO_DB = 'your_database_name'          # Replace with your Odoo database name
ODOO_USER = 'your_username'             # Replace with your PostgreSQL username
ODOO_PASSWORD = 'your_password'         # Replace with your PostgreSQL password

# Connect to Odoo
def connect_to_odoo():
    common = xmlrpc.client.ServerProxy(f'http://{ODOO_HOST}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'http://{ODOO_HOST}/xmlrpc/2/object')
    return uid, models

# PIR Sensor setup
GPIO.setmode(GPIO.BCM)
TRIG_PIN1 = 23  # Trigger pin for ultrasonic sensor
ECHO_PIN1 = 24
LOCK_PIN = 18 
GPIO.setup(TRIG_PIN1, GPIO.OUT)
GPIO.setup(ECHO_PIN1, GPIO.IN)
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

def capture_image1():
    # Capture the image using the camera
    process = Popen(["libcamera-still", "--camera", "0", "--width", "640", "--height", "480", "--timeout", "5000", "-o", "captured.jpg"], stdout=PIPE)
    process.wait()

def perform_ocr(image_path):
    # Load the captured image and convert it from BGR to RGB
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Use Tesseract to OCR the image
    text = pytesseract.image_to_string(image)
    print("Detected Text:", text.strip())
    
    return text.strip()

def check_license_plate(models, uid, detected_text):
    """Check if the detected license plate matches any in the Odoo database."""
    matching_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
                                          'manual.license.plate', 'search',
                                          [[('name', '=', detected_text)]])
    return bool(matching_records)

def write_to_odoo(models, uid, license_plate):
    """Write the detected license plate to the Odoo database."""
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'gate.access', 'create', [{
            'license_plate': license_plate,  # Adjust based on your field name
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),  # Record the timestamp
        }])
        print(f"License plate '{license_plate}' written to Odoo database.")
    except Exception as e:
        print(f"Failed to write to Odoo database: {str(e)}")

try:
    uid, models = connect_to_odoo()
    print("Ultrasonic Sensor Test (CTRL + C to exit)")
    time.sleep(2)
    print("Ready")
    GPIO.output(LOCK_PIN, GPIO.HIGH)  # Activate the relay (lock the door)
    print("Door Locked")
    
    while True:
        distance1 = measure_distance1()
        print(f"Distance1: {distance1:.2f} cm")
        
        if distance1 < 20:  # Adjust distance threshold as needed
            print("Object detected within 20 cm")
            capture_image1()  # Capture image when distance is below threshold
            detected_text = perform_ocr("captured.jpg")  # Perform OCR on the captured image
            
            if detected_text:  # Check if something was detected
                write_to_odoo(models, uid, detected_text)  # Write detected text to Odoo
                if check_license_plate(models, uid, detected_text):  # Check for matches in Odoo
                    GPIO.output(LOCK_PIN, GPIO.LOW)  # Deactivate the relay (unlock the door)
                    print("Gate Unlocked")
                else:
                    print("No match found. Gate remains locked.")
            else:
                print("Nothing detected.")
            
        else:
            print("No object within 20 cm")
            GPIO.output(LOCK_PIN, GPIO.HIGH)  # Lock the door
            print("Door locked")
        
        time.sleep(3)

except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
