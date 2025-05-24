from flask import Flask, render_template, jsonify
import threading
import time
import check_fingerprint  # Import your existing fingerprint functions

app = Flask(__name__)

speed = 60  # Default speed
authenticated = False  # Authentication status

def authenticate_fingerprint():
    """Runs fingerprint authentication every 20 seconds."""
    global authenticated, speed
    while True:
        time.sleep(20)  # Wait 20 seconds before re-authentication
        print("Authenticating fingerprint...")

        if check_fingerprint.get_fingerprint():  # If authentication succeeds
            print("Authentication successful!")
            authenticated = True
        else:
            print("Authentication failed! Reducing speed...")
            authenticated = False
            slow_down()  # Reduce speed to 20 km/h

def slow_down():
    """Gradually reduce speed to 20 km/h."""
    global speed
    while speed > 20:
        speed -= 5  # Reduce speed step by step
        print(f"Speed reducing... {speed} km/h")
        time.sleep(2)  # Slow down gradually every 2 seconds
    print("Speed reduced to 20 km/h.")

@app.route("/")
def home():
    """Render the main UI."""
    return render_template("index.html", speed=speed, authenticated=authenticated)

@app.route("/start_vehicle")
def start_vehicle():
    """Capture the initial fingerprint when the vehicle starts."""
    global authenticated
    print("Starting vehicle... Place your finger on the sensor.")

    if check_fingerprint.enroll_fingerprint(1):  # Store fingerprint at position 1
        print("Fingerprint stored. Vehicle started!")
        authenticated = True
        threading.Thread(target=authenticate_fingerprint, daemon=True).start()
        return jsonify({"status": "success", "message": "Fingerprint recorded, vehicle started!"})
    else:
        return jsonify({"status": "error", "message": "Fingerprint enrollment failed!"})

@app.route("/get_status")
def get_status():
    """Return the vehicle's current status."""
    return jsonify({"speed": speed, "authenticated": authenticated})

if __name__ == "__main__":
    threading.Thread(target=authenticate_fingerprint, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
