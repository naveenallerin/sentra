from ultralytics import YOLO

# Load the pre-trained YOLOv8 nano model (downloads automatically if not present)
model = YOLO('yolov8n.pt')
print("Model downloaded and loaded successfully!")