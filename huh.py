import time
import RPi.GPIO as GPIO
from twilio.rest import Client

# Twilio credentials
account_sid = "AC03f11aaf2a3019eab5a8fb2bc63d98c1"
auth_token = "56d6474d0667f732da5bb69eb8740510"
twilio_number = "+18316619563"  # Your Twilio phone number
receiver_number = "+919361037102"  # Your phone number (for demo)

# GPIO Setup
ALCOHOL_SENSOR_PIN = 25  # MQ-3 DO connected to GPIO 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(ALCOHOL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Internal pull-up resistor

# Initialize Twilio client
client = Client(account_sid, auth_token)

def send_alert():
    message = client.messages.create(
        to=receiver_number,
        from_=twilio_number,
        body="?? DRUNK DRIVING DETECTED! Immediate action required!"
    )
    print(f"Message sent! SID: {message.sid}")

try:
    print("Monitoring alcohol levels...")

    while True:
        alcohol_detected = GPIO.input(ALCOHOL_SENSOR_PIN)

        if alcohol_detected == 0:  # LOW signal means alcohol is detected
            print("?? Alcohol Detected! Sending Alert...")
            send_alert()
            time.sleep(10)  # Avoid spamming messages

        else:
            print("? No Alcohol Detected.")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()

