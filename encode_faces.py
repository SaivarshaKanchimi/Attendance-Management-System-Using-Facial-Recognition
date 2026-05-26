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
    print("❌ No images found")
    exit()

print("Images found:", imgPathList)

imgList = []
studentIDs = []

# ================== LOAD IMAGES ==================
for fileName in imgPathList:

    if not fileName.lower().endswith((".png", ".jpg", ".jpeg")):
        print(f"⚠ Skipping: {fileName}")
        continue

    path = os.path.join(folderPath, fileName)
    img = cv2.imread(path)

    if img is None:
        print(f"⚠ Cannot read: {fileName}")
        continue

    # Resize for speed
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
            print(f"⚠ Multiple faces in {sid}, skipping")

        else:
            print(f"⚠ No face found in {sid}")

    return encodeList, validIDs

# ================== START ==================
print("⏳ Encoding Started...")

encodeListKnown, studentIDs = findEncodings(imgList, studentIDs)

if len(encodeListKnown) == 0:
    print("❌ No valid encodings")
    exit()

# ================== SAVE ==================
with open("EncodeFile.p", "wb") as file:
    pickle.dump([encodeListKnown, studentIDs], file)

print("✅ Encoding Completed Successfully")
print("Total Valid Faces:", len(studentIDs))