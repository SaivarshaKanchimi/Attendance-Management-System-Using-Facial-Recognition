import csv
import os

filename = "students.csv"

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
        "starting_year": 2023,
        "year": 3,
        "standing": "G",
        "total_attendance": 4,
        "last_attendance_time": "2026-01-21 12:33:10",
        "content": "Good student"
    }
]

# Read existing IDs
existing_ids = set()

if os.path.isfile(filename):
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_ids.add(row["id"])

# Write only new data
with open(filename, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())

    if os.stat(filename).st_size == 0:
        writer.writeheader()

    for row in data:
        if row["id"] not in existing_ids:
            writer.writerow(row)
        else:
            print(f"⚠️ ID {row['id']} already exists, skipping...")

print("✅ students.csv updated without duplicates")