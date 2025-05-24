import time
import serial
import adafruit_fingerprint

# Initialize UART serial connection (use /dev/serial0 for Raspberry Pi 3 & 4)
uart = serial.Serial("/dev/serial0", baudrate=57600, timeout=1)

# Initialize the fingerprint sensor
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

def get_fingerprint():
    """Capture a fingerprint and check if it's in the database."""
    print("Place your finger on the sensor...")
    
    while finger.get_image() != adafruit_fingerprint.OK:
        pass  # Wait until a fingerprint is detected

    print("Fingerprint detected, processing...")
    
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Error converting fingerprint image!")
        return

    if finger.finger_search() == adafruit_fingerprint.OK:
        print(f"Match found! ID: {finger.finger_id}, Confidence: {finger.confidence}")
    else:
        print("No match found.")

def enroll_fingerprint(location):
    """Enroll a new fingerprint at the given location ID."""
    print(f"Enrolling a new fingerprint at position {location}. Place your finger on the sensor...")

    for i in range(1, 3):
        while True:
            if finger.get_image() == adafruit_fingerprint.OK:
                break
        print(f"Fingerprint {i} captured.")

        if finger.image_2_tz(i) != adafruit_fingerprint.OK:
            print("Error converting fingerprint image!")
            return

        if i == 1:
            print("Remove your finger and place it again...")
            time.sleep(2)

    if finger.create_model() != adafruit_fingerprint.OK:
        print("Failed to create fingerprint model.")
        return

    if finger.store_model(location) == adafruit_fingerprint.OK:
        print(f"Fingerprint stored successfully at position {location}!")
    else:
        print("Error storing fingerprint.")

def delete_fingerprint(location):
    """Delete a fingerprint from the database."""
    if finger.delete_model(location) == adafruit_fingerprint.OK:
        print(f"Fingerprint at position {location} deleted successfully.")
    else:
        print("Error deleting fingerprint.")

# Main loop
if __name__ == "__main__":
    try:
        while True:
            print("\n1. Capture Fingerprint")
            print("2. Enroll New Fingerprint")
            print("3. Delete Fingerprint")
            print("4. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                get_fingerprint()
            elif choice == "2":
                location = int(input("Enter storage location ID (1-127): "))
                enroll_fingerprint(location)
            elif choice == "3":
                location = int(input("Enter fingerprint ID to delete: "))
                delete_fingerprint(location)
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Try again.")

    except KeyboardInterrupt:
        print("\nProgram terminated.")
