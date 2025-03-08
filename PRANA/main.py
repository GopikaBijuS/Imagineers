from flask import Flask, render_template, Response, request
import cv2
import mediapipe as mp
import numpy as np  # For angle calculations


app = Flask(__name__)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils


def detectPose(image, pose, display=False):
    output_image = image.copy()
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(imageRGB)
    height, width, _ = image.shape
    landmarks = []

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(output_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        for landmark in results.pose_landmarks.landmark:
            landmarks.append((int(landmark.x * width), int(landmark.y * height), (landmark.z * width)))

    return output_image, landmarks


def calculateAngle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def classifyPose(landmarks, output_image, selected_asana, display=False):
    label = "Unknown Pose"
    color = (0, 0, 255)

    if not landmarks or len(landmarks) < 33:
        cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
        return output_image, label

    # Extract key joint angles
    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value], 
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value], 
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])

    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value], 
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value], 
                                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])

    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value], 
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value], 
                                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])

    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value], 
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value], 
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])

    left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value], 
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value], 
                                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])

    right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value], 
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value], 
                                      landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])

    hip_distance = np.linalg.norm(np.array(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value][:2]) - 
                                  np.array(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value][:2])) 

    # Check only the selected asana
    if selected_asana == "Trikonasana":
        if (165 < left_knee_angle < 195 and 165 < right_knee_angle < 195 and 
            130 < left_elbow_angle < 180 and 175 < right_elbow_angle < 220):
            label = "Trikonasana"

    elif selected_asana == "Virabadrasana":
        if (90 < left_knee_angle < 120 and 165 < right_knee_angle < 195):
            label = "Virabadrasana"

    elif selected_asana == "Vrikshasana":
        if (315 < left_knee_angle < 335 or 25 < right_knee_angle < 45):
            label = "Vrikshasana"

    elif selected_asana == "Bhujangasana":
        if (160 < left_elbow_angle < 190 and 160 < right_elbow_angle < 190 and 
            50 < left_shoulder_angle < 80 and 50 < right_shoulder_angle < 80):
            label = "Bhujangasana"

    elif selected_asana == "Sukhasana":
        if (40 < left_knee_angle < 70 and 40 < right_knee_angle < 70 and 
            60 < left_shoulder_angle < 90 and 60 < right_shoulder_angle < 90 and hip_distance < 150):
            label = "Sukhasana"

    elif selected_asana == "Chakrasana":
        if (240 < left_elbow_angle < 280 and 240 < right_elbow_angle < 280 and
            250 < left_knee_angle < 290 and 250 < right_knee_angle < 290):
            label = "Chakrasana"

    # If the correct pose is detected, turn the label green
    if label == selected_asana:
        color = (0, 255, 0)  # Green if pose matches
    else:
        label = "Unknown Pose"

    cv2.putText(output_image, label, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    return output_image, label


def webcam_feed(selected_asana):
    camera_video = cv2.VideoCapture(0)
    camera_video.set(3, 1380)
    camera_video.set(4, 960)

    while camera_video.isOpened():
        ok, frame = camera_video.read()
        if not ok:
            continue

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

        frame, landmarks = detectPose(frame, pose, display=False)

        if landmarks:
            frame, detected_asana = classifyPose(landmarks, frame, selected_asana, display=False)

            # Display Accuracy
            if detected_asana == selected_asana:
                accuracy_text = f"{detected_asana}, 100%"
            else:
                accuracy_text = "Unknown Pose, 0%"

            cv2.putText(frame, accuracy_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

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
    asana = request.args.get('asana', 'Unknown')
    return render_template('yoga_try.html', asana=asana)

@app.route('/video_feed1')
def video_feed1():
    asana = request.args.get('asana', 'Unknown')
    return Response(webcam_feed(asana), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
