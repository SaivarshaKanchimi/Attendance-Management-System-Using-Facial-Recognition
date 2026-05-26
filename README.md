# Attendance-Management-System-Using-Facial-Recognition
A real-time face recognition-based attendance system built with Flask, OpenCV, and the face_recognition library. Students are automatically identified via webcam and their attendance is logged to Google Sheets instantly.



- **Features:**
- 🔍 Real-time face detection & recognition via webcam stream
- 📋 Automatic attendance logging to Google Sheets with timestamp
- 👨‍🎓 Student portal — view personal attendance history after login
- 🛠️ Admin dashboard — add, edit, and delete students with live face re-encoding
- 📁 CSV-based student database — lightweight, no external DB required
- ⚡ Frame-skipping optimization for smooth, low-latency video streaming
- 🚫 Duplicate prevention — each student marked only once per session


 **Tech Stack:**
- Web Framework : Flask
- Face Recognition : face_recognition (dlib), OpenCV
- Attendance Storage : Google Sheets API (gspread)
- Student Records : CSV (students.csv)
- Frontend : HTML5, CSS3, Jinja2 Templates
- Image Encoding : Pickle (.p file)

### ⚙️ Getting Started

**Prerequisites:**

- Python 3.8+
- A working webcam
- A Google Cloud project with Sheets API enabled
- A Google Spreadsheet for attendance logging

👤 Portals
Student Portal (/student_login)

- Login with Student ID, registered email, and password
- View personal profile and total attendance count

Admin Portal (/admin_login)

- View all registered students and their attendance
- Add new students (uploads image + auto re-encodes)
- Edit student details
- Delete students (removes image + re-encodes)

📦 Dependencies
flask
opencv-python
face_recognition
numpy
cvzone
gspread
oauth2client


```bash

#1. Clone the Repository
git clone https://github.com/your-username/attendance-management-facial-recognition.git
cd attendance-management-facial-recognition

# 2. Install Dependencies
pip install -r requirement.txt

# 3. Set Up Google Sheets API

Go to Google Cloud Console and create a new project.
Enable Google Sheets API and Google Drive API.
Create a Service Account, download the JSON key, and save it as credentials.json in the project root.
Create a Google Spreadsheet for attendance. Share it with the service account's email (with Editor access).
In webapp.py, replace the spreadsheet URL with your own:
   sheet = client.open_by_url("YOUR_GOOGLE_SHEET_URL").sheet1

# 4. Add Student Images
Place face images inside static/Files/Images/. Each image must be named after the student's ID:
static/Files/Images/
├── 2310520001.jpg
├── 2310520002.jpg
└── ...

# 5. Generate Face Encodings
bashpython encode_faces.py
This scans the images folder, generates 128-d face encodings, and saves them to EncodeFile.p.

# 6. Run the Application
bashpython webapp.py

Install all via:
bashpip install -r requirement.txt

📄 License
This project is licensed under the MIT License. See license.txt for Details.

