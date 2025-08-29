import cv2
import face_recognition

# Load a known image
known_image = face_recognition.load_image_file("./images/1.png")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    rgb_frame = frame[:, :, ::-1]  # BGR -> RGB

    # Detect all face encodings in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare with known face
        matches = face_recognition.compare_faces([known_encoding], face_encoding)
        name = "Unknown"

        if matches[0]:
            name = "Person 1"

        # Draw bounding box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
