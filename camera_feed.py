import cv2
from ultralytics import YOLO
import csv
from datetime import datetime
from playsound import playsound

def capture_and_detect_with_alerts(source=0, log_file="object_logs.csv", alert_sound="alert_sound.mp3"):
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

                # Log the detection
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

                # Trigger alert for specific objects (simulate vehicles for testing)
                alert_classes = ["person", "tv", "truck", "bus"]  # Add real vehicles when testing outdoors
                if class_name in alert_classes:
                    print(f"ALERT: Detected {class_name}!")
                    try:
                        playsound(alert_sound)  # Play the alert sound
                    except Exception as e:
                        print(f"Error playing sound: {e}")
                        # Fallback: Use macOS text-to-speech
                        import os
                        os.system("say 'Alert!'")

        # Display object count on frame
        cv2.putText(frame, f"Objects: {object_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Show the frame with detections
        cv2.imshow("Camera Feed with Object Detection and Alerts", frame)
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
    capture_and_detect_with_alerts(0)  # Change to RTSP URL when you have one