import cv2
from ultralytics import YOLO
import csv
from datetime import datetime
import requests
import logging

# Configure logging for monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_data_to_backend(data, api_url="http://localhost:3000/api/v1/traffic_data", api_key="my_secret_api_key"):
    """
    Send processed data to the backend using HTTPS POST with API key authentication.

    Args:
        data (dict): Processed data to send (e.g., vehicle/object counts, types).
        api_url (str): Backend API endpoint URL.
        api_key (str): API key for authentication.

    Returns:
        bool: True if data was sent successfully, False otherwise.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=5)
        response.raise_for_status()
        logging.info("Data sent successfully: %s", response.json())
        return True
    except requests.exceptions.RequestException as e:
        logging.error("Failed to send data: %s", e)
        return False

def capture_and_detect_with_streaming(source=0, log_file="object_logs.csv"):
    # Load the YOLOv8 model
    model = YOLO('yolov8n.pt')

    # Connect to the camera or stream
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Couldn’t connect to {source}")
        return

    print(f"Successfully connected to {source}. Press 'q' to quit.")

    # Initialize object counter and log list
    object_count = 0
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
            class_id = int(result.cls[0])  # Class ID
            confidence = float(result.conf[0])  # Confidence score
            class_name = model.names[class_id]  # Get class name (e.g., "person", "tv")

            if confidence > 0.5:  # Confidence threshold
                object_count += 1
                x1, y1, x2, y2 = map(int, result.xyxy[0])  # Bounding box coordinates
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Log the detection locally
                log_entry = {
                    "timestamp": timestamp,
                    "object_type": class_name,
                    "confidence": confidence,
                    "center_x": center_x,
                    "center_y": center_y
                }
                logs.append(log_entry)

                # Draw bounding box and label on frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{class_name} {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Send detection data to backend (simulate vehicles for testing)
                data_to_send = {
                    "timestamp": timestamp,
                    "device_id": "edge_001",  # Simulated edge device ID
                    "object_type": class_name,
                    "confidence": confidence,
                    "location": {"x": center_x, "y": center_y}
                }
                send_data_to_backend(data_to_send)

        # Display object count on frame
        cv2.putText(frame, f"Objects: {object_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Show the frame with detections
        cv2.imshow("Camera Feed with Object Detection and Streaming", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save logs to CSV
    with open(log_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "object_type", "confidence", "center_x", "center_y"])
        writer.writeheader()
        writer.writerows(logs)

    print(f"Logged {object_count} objects to {log_file}")

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Use webcam (0) for testing, or replace with RTSP URL like "rtsp://your_camera_ip/stream"
    capture_and_detect_with_streaming(0)  # Change to RTSP URL when you have one