import cv2
from ultralytics import YOLO
import csv
from datetime import datetime

def capture_and_detect_with_analytics(source=0, log_file="vehicle_logs.csv"):
    # Load the YOLOv8 model
    model = YOLO('yolov8n.pt')

    # Connect to the camera or stream
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Couldn’t connect to {source}")
        return

    print(f"Successfully connected to {source}. Press 'q' to quit.")

    # Initialize vehicle counter and log list
    vehicle_count = 0
    logs = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        # Perform detection
        results = model(frame)

        # Process each detection
        for result in results[0].boxes:
            class_id = int(result.cls[0])  # Class ID (e.g., 2 for car, 7 for truck)
            confidence = float(result.conf[0])  # Confidence score
            class_name = model.names[class_id]  # Get class name (e.g., "car")

            # Only log vehicles (filter by class names)
            vehicle_classes = ["car", "truck", "bus", "motorcycle"]
            if class_name in vehicle_classes and confidence > 0.5:  # Confidence threshold
                vehicle_count += 1
                x1, y1, x2, y2 = map(int, result.xyxy[0])  # Bounding box coordinates
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Log the detection
                log_entry = {
                    "timestamp": timestamp,
                    "vehicle_type": class_name,
                    "confidence": confidence,
                    "center_x": center_x,
                    "center_y": center_y
                }
                logs.append(log_entry)

                # Draw bounding box and label on frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display vehicle count on frame
        cv2.putText(frame, f"Vehicles: {vehicle_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Show the frame with detections
        cv2.imshow("Camera Feed with Vehicle Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save logs to CSV
    with open(log_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "vehicle_type", "confidence", "center_x", "center_y"])
        writer.writeheader()
        writer.writerows(logs)

    print(f"Logged {vehicle_count} vehicles to {log_file}")

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Use webcam (0) for testing, or replace with RTSP URL like "rtsp://your_camera_ip/stream"
    capture_and_detect_with_analytics(0)  # Change to RTSP URL when you have one