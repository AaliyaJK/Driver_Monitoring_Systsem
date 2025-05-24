import cv2

# Open the webcam (0 for the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
else:
    print("Camera is working!")

# Release the camera after use
cap.release()
