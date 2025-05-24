import time
import serial
import threading
import tkinter as tk
from tkinter import PhotoImage
import adafruit_fingerprint
from PIL import Image, ImageTk

# Initialize fingerprint sensor
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# Global Variables
speed = 0
authenticated = False
total_fingers = 3  # Register exactly 3 fingerprints
registered_fingers = 0

# GUI Setup
root = tk.Tk()
root.title("ðŸš— Smart Authentication & Speed Control")
root.geometry("600x500")
root.configure(bg="#1e1e2e")

# GIF Path - You can change this path to your GIF location
gif_path = "/home/raspberrypi/Documents/images"  # Update this path to your GIF file

# Load the GIF
try:
    car_gif = PhotoImage(file=gif_path)
except:
    car_gif = None  # If the GIF is not found, avoid crashing

# Canvas for animated car
canvas = tk.Canvas(root, width=600, height=150, bg="#1e1e2e", highlightthickness=0)
canvas.pack()
car = canvas.create_image(50, 75, anchor="w", image=car_gif) if car_gif else None

# UI Labels
status_label = tk.Label(root, text="ðŸ”’ Registering fingerprints...", font=("Arial", 16, "bold"), bg="#1e1e2e", fg="white")
status_label.pack(pady=10)

speed_label = tk.Label(root, text="Speed: 0 km/h", font=("Arial", 16, "bold"), bg="#1e1e2e", fg="white")
speed_label.pack(pady=10)

entry_label = tk.Label(root, text="Place finger on sensor...", font=("Arial", 12), bg="#1e1e2e", fg="lightgray")
entry_label.pack(pady=5)

# Function to move the car GIF based on speed
def move_car(speed):
    if car_gif:
        canvas.coords(car, 50 + speed * 5, 75)  # Moves car based on speed
    root.update()

# Function to register a fingerprint
def enroll_fingerprint(finger_id):
    global registered_fingers
    print(f"ðŸ“Œ Registering Fingerprint ID {finger_id}")
    status_label.config(text=f"ðŸ“Œ Registering Fingerprint ID {finger_id}")

    for attempt in range(1, 3):  # Two attempts required for registration
        while finger.get_image() != adafruit_fingerprint.OK:
            pass
        if finger.image_2_tz(attempt) != adafruit_fingerprint.OK:
            print("Error processing image, try again.")
            return False

        if attempt == 1:
            print("âœ… First scan done. Remove finger.")
            status_label.config(text="âœ… First scan done. Remove finger.")
            time.sleep(2)

    if finger.create_model() != adafruit_fingerprint.OK:
        print("Error creating fingerprint model!")
        return False

    if finger.store_model(finger_id) != adafruit_fingerprint.OK:
        print("Error storing fingerprint!")
        return False

    print(f"âœ… Fingerprint {finger_id} registered successfully!")
    registered_fingers += 1
    return True

# Function to register 3 fingerprints
def register_fingerprints():
    global registered_fingers
    registered_fingers = 0  # Reset count

    for i in range(1, total_fingers + 1):
        if not enroll_fingerprint(i):
            print("âŒ Registration failed! Restart the app.")
            status_label.config(text="âŒ Registration failed! Restart the app.")
            return False

    print("âœ… All fingerprints registered successfully!")
    status_label.config(text="âœ… Registration Complete! Place a finger to authenticate.", fg="green")
    return True

# Function to authenticate fingerprint
def get_fingerprint():
    global authenticated
    print("Place your finger on the sensor...")

    while finger.get_image() != adafruit_fingerprint.OK:
        pass

    print("Fingerprint detected, processing...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        print("Error converting image!")
        return False

    if finger.finger_search() == adafruit_fingerprint.OK:
        print(f"âœ… Match found! ID: {finger.finger_id}, Confidence: {finger.confidence}")
        authenticated = True
        return True
    else:
        print("âŒ No match found.")
        authenticated = False
        return False

# Function to increase speed
def increase_speed(target_speed):
    global speed
    while speed < target_speed:
        speed += 5
        speed_label.config(text=f"Speed: {speed} km/h")
        move_car(speed)
        time.sleep(0.5)

# Function to decrease speed
def decrease_speed():
    global speed
    while speed > 0:
        speed -= 5
        speed_label.config(text=f"Speed: {speed} km/h")
        move_car(speed)
        time.sleep(0.5)

# Function to handle authentication and speed control
def authenticate_and_control():
    global authenticated

    while True:
        if get_fingerprint():
            status_label.config(text="âœ… Authentication Successful! Car Starting...", fg="green")
            threading.Thread(target=increase_speed, args=(50,)).start()  # Increase speed to 50
        else:
            status_label.config(text="âŒ Authentication Failed! Slowing Down...", fg="red")
            threading.Thread(target=decrease_speed).start()  # Slow down
       
        time.sleep(10)  # Wait for 10 seconds before re-authenticating

        if not get_fingerprint():  # If failed, reduce speed
            status_label.config(text="âš ï¸ Re-authentication Failed! Slowing Down...", fg="orange")
            threading.Thread(target=decrease_speed).start()

# Start registration first
if register_fingerprints():
    # Run authentication in a separate thread
    auth_thread = threading.Thread(target=authenticate_and_control, daemon=True)
    auth_thread.start()

# Run GUI loop
root.mainloop()