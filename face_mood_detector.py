import cv2
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

# Load better facial expression recognition model
processor = AutoImageProcessor.from_pretrained("dima806/facial_emotions_image_detection")
model = AutoModelForImageClassification.from_pretrained("dima806/facial_emotions_image_detection")
model.eval()

# Load OpenCV face detector (Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_mood_from_face_live(confidence_threshold=0.7):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return None

    print("[INFO] Webcam window opened. Detecting mood...")

    mood_detected = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        display_frame = frame.copy()

        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Crop the face region
            face = frame[y:y+h, x:x+w]
            if face.size == 0:
                continue

            # Convert to PIL for model processing
            image = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image)

            # Preprocess and predict
            inputs = processor(images=pil_image, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                top_prob, top_label = torch.max(probs, dim=1)

                confidence = top_prob.item()
                mood = model.config.id2label[top_label.item()]
                label_text = f"{mood} ({confidence:.2f})"

            # Show mood on face rectangle
            cv2.putText(display_frame, label_text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Auto exit if confident
            if confidence >= confidence_threshold:
                print(f"[INFO] Mood '{mood}' detected with confidence {confidence:.2f}. Exiting...")
                mood_detected = mood
                cap.release()
                cv2.destroyAllWindows()
                return mood_detected

        cv2.imshow("Mood Detection (Face Cropping)", display_frame)

        # ESC to exit manually
        if cv2.waitKey(1) & 0xFF == 27:
            print("[INFO] ESC pressed. Exiting without mood detection.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return mood_detected


def gen_frames(confidence_threshold=0.7):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            if face.size == 0:
                continue

            image = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image)

            inputs = processor(images=pil_image, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                top_prob, top_label = torch.max(probs, dim=1)

                confidence = top_prob.item()
                mood = model.config.id2label[top_label.item()]
                label_text = f"{mood} ({confidence:.2f})"

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, label_text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Encode frame for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Run the live detection
if __name__ == "__main__":
    mood = detect_mood_from_face_live()
    if mood:
        print(f"[RESULT] Final detected mood: {mood}")
    else:
        print("[RESULT] No mood detected.")
