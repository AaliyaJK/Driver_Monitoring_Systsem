import cv2
import mediapipe as mp
import pyttsx3
import time
import numpy as np

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

# Load MediaPipe models
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands

face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Eye landmarks (MediaPipe indices)
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]

# Open webcam
cap = cv2.VideoCapture(0)

# Drowsiness tracking
eye_closed_time = None  # Start time when eyes close
drowsiness_threshold = 2  # Alert if eyes stay closed for 2+ seconds
alert_delay = 5  # Delay between voice alerts
last_alert_time = 0  # To avoid spam alerts

# Smooth the EAR calculation
ear_smoothing_factor = 0.9
previous_ear = 0.0

def eye_aspect_ratio(eye_points, landmarks):
    """Calculate Eye Aspect Ratio (EAR) to determine if eyes are closed."""
    A = np.linalg.norm(np.array(landmarks[eye_points[1]]) - np.array(landmarks[eye_points[5]]))
    B = np.linalg.norm(np.array(landmarks[eye_points[2]]) - np.array(landmarks[eye_points[4]]))
    C = np.linalg.norm(np.array(landmarks[eye_points[0]]) - np.array(landmarks[eye_points[3]]))
    EAR = (A + B) / (2.0 * C)
    return EAR

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_face = face_mesh.process(image)
    results_hands = hands.process(image)

    # Convert back to BGR for OpenCV display
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    current_time = time.time()
    face_detected = results_face.multi_face_landmarks is not None
    hands_detected = results_hands.multi_hand_landmarks

    drowsiness_alert = False
    hands_off_wheel_alert = False

    if face_detected:
        for face_landmarks in results_face.multi_face_landmarks:
            h, w, _ = frame.shape
            landmarks = [(int(pt.x * w), int(pt.y * h)) for pt in face_landmarks.landmark]

            # Calculate EAR for both eyes
            left_EAR = eye_aspect_ratio(LEFT_EYE_LANDMARKS, landmarks)
            right_EAR = eye_aspect_ratio(RIGHT_EYE_LANDMARKS, landmarks)
            avg_EAR = (left_EAR + right_EAR) / 2.0

            # Smooth the EAR value
            avg_EAR = ear_smoothing_factor * avg_EAR + (1 - ear_smoothing_factor) * previous_ear
            previous_ear = avg_EAR

            # Detect drowsiness based on EAR threshold
            if avg_EAR < 0.3:  # Adjust this threshold if necessary
                if eye_closed_time is None:
                    eye_closed_time = time.time()  # Start timer
                elif time.time() - eye_closed_time >= drowsiness_threshold:  # Eyes closed too long
                    if current_time - last_alert_time > alert_delay:
                        print("âš  ALERT: DRIVER IS SLEEPING! âš ")
                        cv2.putText(image, "ALERT: DRIVER IS SLEEPING!", (50, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                        engine.say("Wake up! You are drowsy. Stay alert!")
                        engine.runAndWait()
                        last_alert_time = current_time
                        drowsiness_alert = True
            else:
                eye_closed_time = None  # Reset if eyes are open

    # Detect hands
    if hands_detected:
        num_hands = len(results_hands.multi_hand_landmarks)
        if num_hands < 2:  # Less than two hands detected
            if current_time - last_alert_time > alert_delay:
                print("âš  ALERT:HANDS OFF THE WHEEL! âš ")
                cv2.putText(image, "ALERT:HANDS OFF THE WHEEL!", (50, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                engine.say("Put your hands back on the wheel!")
                engine.runAndWait()
                last_alert_time = current_time
                hands_off_wheel_alert = True

    # Display alerts on screen
    if drowsiness_alert:
        cv2.putText(image, "ALERT: DRIVER IS SLEEPING!", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    if hands_off_wheel_alert:
        cv2.putText(image, "ALERT: BOTH HANDS OFF THE WHEEL!", (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Display frame
    cv2.putText(image, "Press 'q' to exit", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow("Driver Monitoring", image)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows() 
