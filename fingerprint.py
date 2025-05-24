import time
import threading
from pyfingerprint.pyfingerprint import PyFingerprint
import tkinter as tk

# Initialize Fingerprint Sensor
try:
    sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if not sensor.verifyPassword():
        raise ValueError("Invalid fingerprint sensor password!")
except Exception as e:
    print("Fingerprint Sensor Error:", e)
    exit(1)
# GUI Speed Control
class SpeedGUI:
    def _init_(self, root):
        self.root = root
        self.root.title("Vehicle Speed Monitor")
        self.speed = 100  # Initial Speed
        self.label = tk.Label(root, text=f"Speed: {self.speed} km/h", font=("Arial", 20))
        self.label.pack()
        self.update_gui()

    def update_gui(self):
        self.label.config(text=f"Speed: {self.speed} km/h")
        self.root.update()

    def reduce_speed(self):
        self.speed = max(20, self.speed - 10)  # Minimum Speed: 20 km/h
        self.update_gui()

    def restore_speed(self):
        self.speed = 100  # Restore to default speed
        self.update_gui()

# Authentication & Speed Control Logic
class AuthenticationSystem:
    def _init_(self, gui):
        self.authenticated_user = None
        self.last_auth_time = None
        self.gui = gui

    def authenticate_fingerprint(self):
        """Function to authenticate fingerprint and update speed"""
        print("Place your finger...")
        while not sensor.readImage():
            pass  # Wait for a valid fingerprint input

        sensor.convertImage(0x01)
        result = sensor.searchTemplate()
        position_number = result[0]

        if position_number >= 0:
            print("Authenticated! Fingerprint ID:", position_number)
            self.authenticated_user = position_number
            self.last_auth_time = time.time()
            self.gui.restore_speed()  # Restore speed
        else:
            print("Fingerprint not recognized!")

    def monitor_authentication(self):
        """Function to check authentication every 10 seconds"""
        while True:
            if self.last_auth_time and (time.time() - self.last_auth_time) > 10:
                print("Re-authentication required!")
                self.gui.reduce_speed()  # Reduce speed if not authenticated
            time.sleep(2)  # Check every 2 seconds

# Main Function
if _name_ == "_main_":
    root = tk.Tk()
    gui = SpeedGUI(root)
    auth_system = AuthenticationSystem(gui)

    # Start monitoring authentication in a separate thread
    monitor_thread = threading.Thread(target=auth_system.monitor_authentication, daemon=True)
    monitor_thread.start()

    # Main authentication loop
    while True:
        auth_system.authenticate_fingerprint()
        time.sleep(2)  # Small delay to avoid immediate re-authentication
