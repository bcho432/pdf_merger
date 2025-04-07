from flask import Flask, request, jsonify
import cv2
import numpy as np
from deepface import DeepFace
import os

app = Flask(__name__)

# Load YOLO model
net = cv2.dnn.readNet("yolo_files/yolov3.weights", "yolo_files/yolov3.cfg")
with open("yolo_files/coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# Set up YOLO output layers
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def detect_faces(image_path):
    # Load image
    img = cv2.imread(image_path)
    height, width, channels = img.shape

    # Prepare image for YOLO
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Extract face bounding boxes
    faces = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and classes[class_id] == "person":  # YOLO detects "person" class
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                faces.append((x, y, w, h))

    return faces, img

def compare_faces(img1_path, img2_path):
    # Detect faces in both images
    faces1, img1 = detect_faces(img1_path)
    faces2, img2 = detect_faces(img2_path)

    if not faces1 or not faces2:
        return {"error": "No faces detected in one or both images."}

    # Extract the first detected face (you can modify to handle multiple faces)
    x1, y1, w1, h1 = faces1[0]
    x2, y2, w2, h2 = faces2[0]

    face1 = img1[y1:y1+h1, x1:x1+w1]
    face2 = img2[y2:y2+h2, x2:x2+w2]

    # Save the cropped faces temporarily
    cv2.imwrite("face1.jpg", face1)
    cv2.imwrite("face2.jpg", face2)

    # Compare faces using DeepFace
    result = DeepFace.verify("face1.jpg", "face2.jpg")
    return result

@app.route('/compare', methods=['POST'])
def compare():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Please upload two images."}), 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    # Save the uploaded files temporarily
    file1_path = "upload1.jpg"
    file2_path = "upload2.jpg"
    file1.save(file1_path)
    file2.save(file2_path)

    # Compare faces
    result = compare_faces(file1_path, file2_path)

    # Clean up
    os.remove(file1_path)
    os.remove(file2_path)
    if os.path.exists("face1.jpg"):
        os.remove("face1.jpg")
    if os.path.exists("face2.jpg"):
        os.remove("face2.jpg")

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)