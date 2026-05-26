import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime
from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)

# ================== CAMERA ==================
capture = cv2.VideoCapture(0)
if not capture.isOpened():
    print("❌ Camera not accessible")
    exit()

capture.set(3, 640)
capture.set(4, 480)

# ================== BACKGROUND ==================
bg_path = "static/Files/Resources/background.png"
imgBackground = cv2.imread(bg_path)

# ================== MODES ==================
folderModePath = "static/Files/Resources/Modes"
imgModeList = [cv2.imread(os.path.join(folderModePath, f))
               for f in sorted(os.listdir(folderModePath))]

# ================== ENCODINGS ==================
with open("EncodeFile.p", "rb") as file:
    encodedFaceKnown, studentIds = pickle.load(file)

# ================== REAL STUDENT DATA ==================
students = {
    "2310520010": {
        "name": "Susanna Shanica",
        "roll": "2310520010",
        "major": "Cloud Security",
        "total_attendance": 0,
        "last_attendance_time": "2024-01-01 00:00:00"
    }
}

# ================== VARIABLES ==================
modeType = 0
counter = 0
id = None
studentInfo = None
imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)

# ================== MAIN LOOP ==================
while True:
    success, img = capture.read()
    if not success:
        break

    imgSmall = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    faceLocations = face_recognition.face_locations(imgSmall)
    faceEncodings = face_recognition.face_encodings(imgSmall, faceLocations)

    imgBackground[162:642, 55:695] = img
    imgBackground[44:677, 808:1222] = imgModeList[modeType]

    if faceLocations:
        for encodeFace, faceLoc in zip(faceEncodings, faceLocations):

            matches = face_recognition.compare_faces(encodedFaceKnown, encodeFace)
            distances = face_recognition.face_distance(encodedFaceKnown, encodeFace)
            matchIndex = np.argmin(distances)

            y1, x2, y2, x1 = [v * 4 for v in faceLoc]

            bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
            cvzone.cornerRect(imgBackground, bbox)

            if matches[matchIndex]:
                id = studentIds[matchIndex]

                if id in students:
                    studentInfo = students[id]
                    counter = 1
                    modeType = 1

    # ================== ATTENDANCE ==================
    if counter == 1 and studentInfo is not None:

        last_time = datetime.strptime(
            studentInfo["last_attendance_time"], "%Y-%m-%d %H:%M:%S"
        )

        if (datetime.now() - last_time).total_seconds() > 30:
            studentInfo["total_attendance"] += 1
            studentInfo["last_attendance_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        else:
            modeType = 3
            counter = 0

    # ================== DISPLAY ==================
    if counter > 0 and studentInfo is not None:

        # Name
        cv2.putText(imgBackground, studentInfo["name"],
                    (820, 445), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

        # Roll Number
        cv2.putText(imgBackground, f"ID: {studentInfo['roll']}",
                    (820, 480), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)

        # Student Image
        imgPath = f"static/Files/Images/{studentInfo['roll']}.jpg"
        if os.path.exists(imgPath):
            imgStudent = cv2.imread(imgPath)

        imgStudentResize = cv2.resize(imgStudent, (216, 216))
        imgBackground[175:391, 909:1125] = imgStudentResize

        counter += 1
        if counter >= 20:
            counter = 0
            modeType = 0

    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) == ord("q"):
        break

capture.release()
cv2.destroyAllWindows()
