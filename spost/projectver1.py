from reference import *

# Setup for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'



try:
    print("Ultrasonic Sensor Test (CTRL + C to exit)")
    time.sleep(2)
    print("Ready")
    GPIO.output(LOCK_PIN, GPIO.HIGH)  # Activate the relay (lock the door)
    print("Door Locked")
    
    while True:
        distance1 = measure_distance1()
        print(f"Distance1: {distance1:.2f} cm")
        distance2 = measure_distance2()
        print(f"Distance2: {distance2:.2f} cm")
        # Lock or unlock the door based on the distance
#         trigger_door_lock(distance)
        
        if distance1 < 5:
            print("Object detected within 5 cm")
            capture_image1()  # Capture image when distance is below 5 cm
            detected_text = perform_ocr("captured.jpg")  # Perform OCR on the captured image
            check_for_match(detected_text, "a3.txt")  # Compare the text with a1.txt
            
        else:
            print("No object within 5 cm")
            GPIO.output(LOCK_PIN, GPIO.HIGH)
            
        if distance2 < 5:
            print("Object detected within 5 cm")
            capture_image2()  # Capture image when distance is below 5 cm
            detected_text = perform_ocr("captured.jpg")  # Perform OCR on the captured image
            check_for_match(detected_text, "a3.txt")  # Compare the text with a1.txt
            
        else:
            print("No object within 5 cm")
            GPIO.output(LOCK_PIN, GPIO.HIGH)
            
        time.sleep(3)

except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()