import subprocess
import sys

def install(name):
    subprocess.call([sys.executable, '-m', 'pip', 'install', name])

install("opencv-python")
install("mediapipe")

import cv2
import mediapipe as mp
import math
import socket
import time 

# Constants
####################################
RASPBERRY_PICO_IP = "192.158.1.113"#
PORT = 12345                       #
####################################
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 1
FONT_COLOR = (0, 0, 255)
RECTANGLE_COLOR = (0, 255, 0)
CENTER_DOT_COLOR = (0, 0, 255)
TEXT_OFFSET = 30
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=MIN_DETECTION_CONFIDENCE, min_tracking_confidence=MIN_TRACKING_CONFIDENCE)

# Define torso landmark IDs
torso_landmarks = [mp_pose.PoseLandmark.LEFT_SHOULDER,
                   mp_pose.PoseLandmark.RIGHT_SHOULDER,
                   mp_pose.PoseLandmark.LEFT_HIP,
                   mp_pose.PoseLandmark.RIGHT_HIP]

# Initialize inside flag
inside = False

# Initialize constants
cap = cv2.VideoCapture(0)
_, frame = cap.read()
(h, w) = frame.shape[:2]
truecen = (w // 2, h // 2)

while cap.isOpened():
    # Read frame
    _, frame = cap.read()
    if not _:
        break

    try:
        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Draw "crosshair"
        cv2.circle(frame, truecen, 7, CENTER_DOT_COLOR, 1)

        # Process the frame for pose detection
        pose_results = pose.process(frame_rgb)

        # Detect a single person and calculate bounding box coordinates for the torso
        if pose_results.pose_landmarks and len(pose_results.pose_landmarks.landmark) == 33:
            landmarks = pose_results.pose_landmarks.landmark
            min_x, min_y, max_x, max_y = w, h, 0, 0

            for landmark in torso_landmarks:
                x, y = int(landmarks[landmark].x * w), int(landmarks[landmark].y * h)

                # Update min and max coordinates
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

            # Calculate angles to turn the camera
            vertical_angle = math.degrees(math.atan((truecen[1] - (min_y + max_y) / 2) / h))
            horizontal_angle = math.degrees(math.atan((truecen[0] - (min_x + max_x) / 2) / w))
            
            # Convert angles to strings for cv2.putText
            vertical_angle_str = str(round(vertical_angle, 1))
            horizontal_angle_str = str(round(horizontal_angle, 1))
            
            #Send instructions to Raspberry Pi
            hsend = 'h' + horizontal_angle_str
            vsend = 'v' + vertical_angle_str

            # Draw angles on the frame
            cv2.putText(frame, vertical_angle_str, (30, TEXT_OFFSET), FONT, FONT_SIZE, FONT_COLOR, 1)
            cv2.putText(frame, horizontal_angle_str, (30, TEXT_OFFSET * 2), FONT, FONT_SIZE, FONT_COLOR, 1)

            # Draw bounding box around the torso
            cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), RECTANGLE_COLOR, 2)

            # Check if the center dot is inside the bounding box
            if min_x <= truecen[0] <= max_x and min_y <= truecen[1] <= max_y:
                inside = True
                cv2.putText(frame, "COLISHUN", (30, TEXT_OFFSET * 3), FONT, FONT_SIZE, FONT_COLOR, 1)
                csend = 'c'
                sock.sendto(csend.encode(), (RASPBERRY_PICO_IP, PORT))
            else: 
                sock.sendto(vsend.encode(), (RASPBERRY_PICO_IP, PORT))
                time.sleep(0.05)
                sock.sendto(hsend.encode(), (RASPBERRY_PICO_IP, PORT))
        # Display the frame
        cv2.imshow('Output', frame)
    
    except cv2.error as e:
        print(f"OpenCV error occurred: {str(e)}")
        break
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        break

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()