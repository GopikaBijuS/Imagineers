from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import math
import numpy as np  # Added NumPy

app = Flask(__name__)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6, model_complexity=1)  # Increased confidence
mp_drawing = mp.solutions.drawing_utils

def detectPose(image, pose, display=False):
    output_image = image.copy()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)
    height, width, _ = image.shape
    landmarks = []
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks, connections=mp_pose.POSE_CONNECTIONS)
        for landmark in results.pose_landmarks.landmark:
            landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))
    return output_image, landmarks

def calculateAngle(a, b, c):
    a = np.array(a); b = np.array(b); c = np.array(c)
    ba = a - b; bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def classifyPose(landmarks, output_image, display=False):
    label = 'Unknown Pose'
    color = (0, 0, 255)

    if not landmarks or len(landmarks) < 33:  # Check for valid landmarks
        cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
        return output_image, label

    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value], landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value], landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])
    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value], landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])
    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value], landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])
    left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value], landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value], landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])
    right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value], landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value], landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])

    hip_distance = np.linalg.norm(np.array(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value][:2]) - np.array(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value][:2])) # hip distance.

    if (165 < left_knee_angle < 195) and (165 < right_knee_angle < 195) and (130 < left_elbow_angle < 180) and (175 < right_elbow_angle < 220) and (100 < left_shoulder_angle < 200) and (50 < right_shoulder_angle < 130):
        label = 'T Pose'
    elif left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195 and left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:
        if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:
            if left_knee_angle > 90 and left_knee_angle < 120 or right_knee_angle > 90 and right_knee_angle < 120:
                label = 'Warrior II Pose'
    elif left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195 and (left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45):
        label = 'Tree Pose'
    elif left_knee_angle < 30 and right_knee_angle < 30 and left_shoulder_angle > 100 and left_shoulder_angle < 130 and right_shoulder_angle > 100 and right_shoulder_angle < 130:
        label = 'Balasana'
    elif left_elbow_angle > 160 and left_elbow_angle < 190 and right_elbow_angle > 160 and right_elbow_angle < 190 and left_shoulder_angle > 50 and left_shoulder_angle < 80 and right_shoulder_angle > 50 and right_shoulder_angle < 80:
        label = 'Bhujangasana'
    elif left_elbow_angle > 240 and left_elbow_angle < 280 and right_elbow_angle > 240 and right_elbow_angle < 280 and left_knee_angle > 250 and left_knee_angle < 290 and right_knee_angle > 250 and right_knee_angle < 290:
        label = 'Chakrasana'
    elif left_knee_angle > 140 and left_knee_angle < 170 and right_knee_angle > 140 and right_knee_angle < 170 and left_shoulder_angle > 120 and left_shoulder_angle < 150 and right_shoulder_angle > 120 and right_shoulder_angle < 150:
        label = 'Naukasana'
    elif left_knee_angle > 170 and left_knee_angle < 190 and right_knee_angle > 170 and right_knee_angle < 190 and left_elbow_angle > 170 and left_elbow_angle < 190 and right_elbow_angle > 170 and right_elbow_angle < 190:
        label = 'Shavasana'
    elif left_knee_angle > 40 and left_knee_angle < 70 and right_knee_angle > 40 and right_knee_angle < 70 and left_shoulder_angle > 60 and left_shoulder_angle < 90 and right_shoulder_angle > 60 and right_shoulder_angle < 90 and hip_distance < 150: #added hip distance.
        label = 'Sukhasana'

    if label != 'Unknown Pose':
        color = (0, 255, 0)
    cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    return output_image, label

def webcam_feed():
    # Initialize the VideoCapture object to read from the webcam
    camera_video = cv2.VideoCapture(0)
    camera_video.set(3, 1380)
    camera_video.set(4, 960)

    while camera_video.isOpened():
        # Read a frame
        ok, frame = camera_video.read()

        if not ok:
            continue

        # Flip the frame horizontally for natural (selfie-view) visualization
        frame = cv2.flip(frame, 1)

        # Get the width and height of the frame
        frame_height, frame_width, _ = frame.shape

        # Resize the frame while keeping the aspect ratio
        frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

        # Perform Pose landmark detection
        frame, landmarks = detectPose(frame, pose, display=False)

        if landmarks:
            # Perform the Pose Classification
            frame, _ = classifyPose(landmarks, frame, display=False)

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera_video.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/yoga_try')
def yoga_try():
    return render_template('yoga_try.html')

@app.route('/video_feed1')
def video_feed1():
    return Response(webcam_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)