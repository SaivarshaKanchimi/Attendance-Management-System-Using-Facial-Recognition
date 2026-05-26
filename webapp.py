from flask import Flask, render_template, Response, redirect, url_for, request
import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime
import json
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1xqWi7wJWXN_GpbaZ99fjzp23dEn7Rwpdyzo0P_p5-9w/edit?usp=sharing").sheet1
ADMIN_ID = "Shanica"
ADMIN_EMAIL = "shanicabolleddu@gmail.com"
ADMIN_PASSWORD = "123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "students.csv")


import csv


last_detected_id = None
last_detected_name = ""
last_face_location = None
display_counter = 0

capture = cv2.VideoCapture(0)  # ✅ natural default camera

# Optional (keep small for speed)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

marked_ids = set()

def update_attendance_cloud(student_id, name):
    if student_id in marked_ids:
        return

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([student_id, name, now])
        marked_ids.add(student_id)
    except:
        print("⚠ Google Sheet error")

def read_students():
    students = {}
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students[row["id"]] = row
    return students



def write_students(students):
    fieldnames = students[next(iter(students))].keys()
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students.values())


def add_student_csv(student_data):
    students = read_students()
    students[student_data["id"]] = student_data
    write_students(students)


def update_student_csv(student_id, updated_data):
    students = read_students()
    if student_id in students:
        students[student_id].update(updated_data)
        write_students(students)


def delete_student_csv(student_id):
    students = read_students()
    if student_id in students:
        del students[student_id]
        write_students(students)

# import firebase_admin
# from firebase_admin import credentials, db


app = Flask(__name__)  # initializing


# database credentials
# cred = credentials.Certificate("serviceAccountKey.json")

# firebase_admin.initialize_app(
    # cred,
    # {
        # "databaseURL": "https://attendance-management-sy-a42cd.firebaseio.com"
    #},
#)


def dataset(id):
    students = read_students()

    if id not in students:
        return None, None, None

    studentInfo = students[id]

    # convert numeric fields
    studentInfo["year"] = int(studentInfo["year"])
    studentInfo["starting_year"] = int(studentInfo["starting_year"])
    studentInfo["total_attendance"] = int(studentInfo["total_attendance"])

    # load student image
    img_path = f"./static/Files/Images/{id}.jpg"
    imgStudent = cv2.imread(img_path)

    # calculate time elapsed
    last_time = datetime.strptime(
        studentInfo["last_attendance_time"], "%Y-%m-%d %H:%M:%S"
    )
    secondsElapsed = (datetime.now() - last_time).total_seconds()

    return studentInfo, imgStudent, secondsElapsed


already_marked_id_student = []
already_marked_id_admin = []



def generate_frame():
    global capture
    global last_detected_id, last_detected_name, last_face_location, display_counter

    # Load encodings once
    with open("EncodeFile.p", "rb") as file:
        encodedFaceKnown, studentIDs = pickle.load(file)

    student_cache = {}
    frame_count = 0

    while True:
        success, img = capture.read()
        if not success:
            print("❌ Camera not working")
            break

        img = cv2.flip(img, 1)
        frame_count += 1

        # ⚡ Skip frames for speed
        if frame_count % 2 != 0:
            if display_counter > 0 and last_face_location is not None:
                y1, x2, y2, x1 = last_face_location
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                text = f"{last_detected_name} ({last_detected_id})"
                cv2.putText(img, text, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 0), 2)

                display_counter -= 1

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            continue

        # 🔍 Face detection
        imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

        faceLocations = face_recognition.face_locations(imgSmall, model="hog")
        faceEncodings = face_recognition.face_encodings(imgSmall, faceLocations)

        for encodeFace, faceLoc in zip(faceEncodings, faceLocations):

            distances = face_recognition.face_distance(encodedFaceKnown, encodeFace)
            matchIndex = np.argmin(distances)

            print("Distance:", distances[matchIndex])  # DEBUG

            if distances[matchIndex] < 0.6:   # 👈 important fix
                id = studentIDs[matchIndex]

                if id not in student_cache:
                    student_cache[id] = dataset(id)

                studentInfo, _, _ = student_cache[id]

                if studentInfo:
                    last_detected_id = id
                    last_detected_name = studentInfo["name"]
                    last_face_location = faceLoc
                    display_counter = 20

                    update_attendance_cloud(id, studentInfo["name"])

        # 👇 Always show stored result (no blinking)
        if display_counter > 0 and last_face_location is not None:
            y1, x2, y2, x1 = last_face_location
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"{last_detected_name} ({last_detected_id})"
            cv2.putText(img, text, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

            display_counter -= 1

        # Stream frame
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


#########################################################################################################################


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video")
def video():
    return Response(
        generate_frame(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


#########################################################################################################################


@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    id = request.form.get("id_number", False)
    email = request.form.get("email", False)
    password = request.form.get("password", False)
    studentIDs, _ = add_image_database()

    if id:
        if id not in studentIDs:
            return render_template(
                "student_login.html", data=" ❌ The id is not registered"
            )

        studentInfo, _, _ = dataset(id)

        if studentInfo is None:
            return render_template(
                "student_login.html", data=" ❌ Student not found in database"
            )

        if studentInfo["password"] == password and studentInfo["email"] == email:
            return redirect(url_for("student", data=id, title="ok"))
        else:
            return render_template(
                "student_login.html", data=" ❌ Email/Password Incorrect"
            )

    return render_template("student_login.html")



@app.route("/student/<data>/<title>")
def student(data, title=None):
    studentInfo, imgStudent, secondElapsed = dataset(data)
    hoursElapsed = round((secondElapsed / 3600), 2)

    info = {
        "studentInfo": studentInfo,
        "lastlogin": hoursElapsed,
        "image": imgStudent,
    }
    return render_template("student.html", data=info)


@app.route("/student_attendance_list")
def student_attendance_list():
    unique_id_student = list(set(already_marked_id_student))
    student_info = []
    for i in unique_id_student:
        student_info.append(dataset(i))
    return render_template("student_attendance_list.html", data=student_info)

@app.route("/admin/admin_attendance_list", methods=["GET", "POST"])
def admin_attendance_list():
    unique_id_admin = list(set(already_marked_id_admin))
    student_info = []

    for sid in unique_id_admin:
        studentInfo, imgStudent, secondElapsed = dataset(sid)
        if studentInfo is None:
            continue
        student_info.append((studentInfo, imgStudent, secondElapsed))

    return render_template("admin_attendance_list.html", data=student_info)


#########################################################################################################################


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        id = request.form.get("id_number")
        email = request.form.get("email")
        password = request.form.get("password")

        if (
            id == "Shanica"
            and email == "shanicabolleddu@gmail.com"
            and password == "123"
             ):
            return redirect(url_for("admin"))
        else:
            return render_template(
                "admin_login.html",
                data="❌ Invalid Admin Credentials"
            )

    return render_template("admin_login.html")




@app.route("/admin")
def admin():
    all_student_info = []
    studentIDs, _ = add_image_database()

    for sid in studentIDs:
        studentInfo, imgStudent, secondElapsed = dataset(sid)

        # 🔐 Skip if student not found in CSV
        if studentInfo is None:
            continue

        all_student_info.append(
            (studentInfo, imgStudent, secondElapsed)
        )

    return render_template("admin.html", data=all_student_info)




#########################################################################################################################

def add_image_database():
    folderPath = "./static/Files/Images"
    imgPathList = os.listdir(folderPath)
    imgList = []
    studentIDs = []

    for path in imgPathList:
        img = cv2.imread(os.path.join(folderPath, path))
        if img is None:
            continue

        imgList.append(img)
        studentIDs.append(os.path.splitext(path)[0])

    return studentIDs, imgList


def findEncodings(images):
    encodeList = []

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


@app.route("/admin/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        id = request.form.get("id")
        name = request.form.get("name")
        password = request.form.get("password")
        dob = request.form.get("dob")
        city = request.form.get("city")
        country = request.form.get("country")
        phone = request.form.get("phone")
        email = request.form.get("email")
        major = request.form.get("major")
        starting_year = int(request.form.get("starting_year"))
        standing = request.form.get("standing")
        total_attendance = int(request.form.get("total_attendance"))
        year = int(request.form.get("year"))
        last_attendance_date = request.form.get("last_attendance_date")
        last_attendance_time = request.form.get("last_attendance_time")
        content = request.form.get("content")

        address = f"{city}, {country}"
        last_attendance_datetime = f"{last_attendance_date} {last_attendance_time}:00"

        # ---------- SAVE IMAGE ----------
        image = request.files["image"]
        image_path = f"./static/Files/Images/{id}.jpg"
        image.save(image_path)

        # ---------- SAVE TO CSV ----------
        add_student_csv({
            "id": id,
            "name": name,
            "password": password,
            "email": email,
            "phone": phone,
            "dob": dob,
            "address": address,
            "major": major,
            "starting_year": starting_year,
            "year": year,
            "standing": standing,
            "total_attendance": total_attendance,
            "last_attendance_time": last_attendance_datetime,
            "content": content
        })

        # ---------- UPDATE ENCODINGS ----------
        studentIDs, imgList = add_image_database()
        encodeListKnown = findEncodings(imgList)

        with open("EncodeFile.p", "wb") as file:
            pickle.dump([encodeListKnown, studentIDs], file)

        return redirect(url_for("admin"))

    return render_template("add_user.html")


#########################################################################################################################


@app.route("/admin/edit_user", methods=["POST", "GET"])
def edit_user():
    value = request.form.get("edit_student")

    studentInfo, imgStudent, secondElapsed = dataset(value)
    hoursElapsed = round((secondElapsed / 3600), 2)

    info = {
        "studentInfo": studentInfo,
        "lastlogin": hoursElapsed,
        "image": imgStudent,
    }

    return render_template("edit_user.html", data=info)


#########################################################################################################################


@app.route("/admin/save_changes", methods=["POST", "GET"])
def save_changes():
    content = request.get_data()

    dic_data = json.loads(content.decode("utf-8"))

    dic_data = {k: v.strip() for k, v in dic_data.items()}

    dic_data["year"] = int(dic_data["year"])
    dic_data["total_attendance"] = int(dic_data["total_attendance"])
    dic_data["starting_year"] = int(dic_data["starting_year"])

    update_student_csv(dic_data["id"], dic_data)
    return "Data updated successfully"


#########################################################################################################################


def delete_image(student_id):
    filepath = f"./static/Files/Images/{student_id}.png"

    if os.path.exists(filepath):
        os.remove(filepath)

    return "Successful"


@app.route("/admin/delete_user", methods=["POST", "GET"])
def delete_user():
    content = request.get_data()

    student_id = json.loads(content.decode("utf-8"))

    delete_student_csv(student_id)
    delete_image(student_id)


    studentIDs, imgList = add_image_database()

    encodeListKnown = findEncodings(imgList)

    encodeListKnownWithIds = [encodeListKnown, studentIDs]

    file = open("EncodeFile.p", "wb")
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

    return "Successful"


#########################################################################################################################
if __name__ == "__main__":
    app.run(debug=True)
