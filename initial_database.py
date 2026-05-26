import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "students.csv")

data = [
    {
        "id": "2310520010",
        "name": "Susanna Shanica",
        "password": "10",
        "email": "2310520010@klh.edu.in",
        "phone": "8341303550",
        "dob": "2006-02-23",
        "address": "Hyderabad, India",
        "major": "Cloud Security",
        "starting_year": "2023",
        "year": "3",
        "standing": "G",
        "total_attendance": "4",
        "last_attendance_time": "2026-01-21 12:33:00",
        "content": "Good student",
    }
]

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("students.csv created successfully at:", CSV_FILE)