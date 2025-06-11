import cv2
import numpy as np
from mtcnn import MTCNN
from tensorflow.keras.models import load_model
from efficientnet.tfkeras import preprocess_input

# Load the trained model
model_path = 'best_model.h5'
loaded_model = load_model(model_path)

# Set the input size expected by the model
INPUT_SIZE = 128

def preprocess_image(img):
    """
    Resize and preprocess an image for model prediction.
    """
    img = cv2.resize(img, (INPUT_SIZE, INPUT_SIZE))
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return img

def predict_face(face_image):
    """
    Predict whether the detected face is Real or Fake.
    Returns class label and confidence score.
    """
    img = preprocess_image(face_image)
    prediction = loaded_model.predict(img)[0, 0]  # Get scalar prediction

    if prediction > 0.5:
        class_label = "Real"
        confidence = prediction
    else:
        class_label = "Fake"
        confidence = 1 - prediction

    return class_label, confidence

def process_image(image_path, output_path):
    """
    Detects faces in the image, classifies them, annotates and saves output image.
    Returns last label text or a message if no faces detected.
    """
    frame = cv2.imread(image_path)

    if frame is None:
        raise ValueError("Could not read image. Check the file path.")

    detector = MTCNN()
    faces = detector.detect_faces(frame)

    if not faces:
        print("No faces detected.")
        cv2.imwrite(output_path, frame)
        return "No faces detected"

    for face in faces:
        bounding_box = face['box']
        detection_confidence = face['confidence']

        if detection_confidence > 0.60:
            x, y, w, h = bounding_box
            face_image = frame[y:y+h, x:x+w]

            class_label, confidence = predict_face(face_image)

            label_text = f"{class_label} ({confidence * 100:.2f}%)"
            label_color = (0, 255, 0) if class_label == "Real" else (0, 0, 255)

            cv2.putText(frame, label_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, label_color, 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), label_color, 2)

    cv2.imwrite(output_path, frame)
    return label_text