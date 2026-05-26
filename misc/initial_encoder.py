import cv2
import pickle
import face_recognition
import os

folderPath = "static/Files/Images"

if not os.path.exists(folderPath):
    print("❌ Image folder not found:", folderPath)
    exit()

imgPathList = os.listdir(folderPath)

if len(imgPathList) == 0:
    print("❌ No images found in folder")
    exit()

print("Images found:", imgPathList)

imgList = []
studentIDs = []

# ================== LOAD IMAGES ==================
for fileName in imgPathList:
    filePath = os.path.join(folderPath, fileName)

    if not fileName.lower().endswith((".png", ".jpg", ".jpeg")):
        print(f"⚠ Skipping non-image file: {fileName}")
        continue

    img = cv2.imread(filePath)

    if img is None:
        print(f"⚠ Unable to read image: {fileName}")
        continue

    # Resize image (faster processing)
    img = cv2.resize(img, (0, 0), None, 0.5, 0.5)

    imgList.append(img)
    studentIDs.append(os.path.splitext(fileName)[0])

print("Student IDs:", studentIDs)

# ================== ENCODING FUNCTION ==================
def findEncodings(images, ids):
    encodeList = []
    validIDs = []

    for img, sid in zip(images, ids):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(imgRGB)
        encodes = face_recognition.face_encodings(imgRGB, face_locations)

        if len(encodes) == 1:
            encodeList.append(encodes[0])
            validIDs.append(sid)

        elif len(encodes) > 1:
            print(f"⚠ Multiple faces found in image: {sid}, skipping...")

        else:
            print(f"⚠ No face detected in image: {sid}")

    return encodeList, validIDs

# ================== START ENCODING ==================
print("⏳ Encoding Started...")
encodeListKnown, studentIDs = findEncodings(imgList, studentIDs)

if len(encodeListKnown) == 0:
    print("❌ No valid face encodings found")
    exit()

# ================== SAVE TO PICKLE ==================
with open("EncodeFile.p", "wb") as file:
    pickle.dump([encodeListKnown, studentIDs], file)

print("✅ Encoding Completed Successfully")
print("Total Faces Encoded:", len(studentIDs))