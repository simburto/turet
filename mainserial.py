import subprocess
import sys

try: 
  if open('cache.txt', 'r').read() != '1':
    packages = open('requirements.txt', 'r').read().splitlines()
    print("installing dependencies")
    for i in range(len(packages)):
      subprocess.check_call([sys.executable, "-m", "pip", "install", packages[i]])
    with open('cache.txt', 'w') as f:
      f.write('1')
except:
  open('cache.txt', 'w')
  print("created cache file")
  print("installing dependencies")
  packages = open('requirements.txt', 'r').read().splitlines()
  for i in range(len(packages)):
    subprocess.check_call([sys.executable, "-m", "pip", "install", packages[i]])
  with open('cache.txt', 'w') as f:
    f.write('1')
import cv2
import mediapipe as mp
import math
import serial
import time 

MIN_DETECTION_CONFIDENCE = 0.8
MIN_TRACKING_CONFIDENCE = 0.4
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 1
FONT_COLOR = (0, 0, 255)
RECTANGLE_COLOR = (0, 255, 0)
CENTER_DOT_COLOR = (0, 0, 255)
TEXT_OFFSET = 30

ser = serial.Serial('COM4', 9600)

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
            mp_drawing.draw_landmarks(
            frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
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
                csend = 'c00000'
                print(csend)
                ser.write(csend.encode())
                time.sleep(0.05)
            else: 
                while len(vsend) < 6:
                    vsend = vsend + '0'
                print(vsend)
                ser.write(vsend.encode())
                time.sleep(0.05)
                while len(hsend) < 6:
                    hsend = hsend + '0'
                print(hsend)
                print(ser.write(hsend.encode()))
        else:
            ser.write('banana'.encode())
            print('banana')
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