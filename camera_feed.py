import cv2
from ultralytics import YOLO

def capture_and_detect(source=0):  # Default to webcam (0), can use RTSP URL
    # Load the YOLOv8 model
    model = YOLO('yolov8n.pt')

    # Connect to the camera or stream
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Error: Couldn’t connect to {source}")
        return

    print(f"Successfully connected to {source}. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        # Perform detection
        results = model(frame)

        # Draw detections on the frame
        annotated_frame = results[0].plot()

        # Show the frame with detections
        cv2.imshow("Camera Feed with Vehicle Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Use webcam (0) for testing, or replace with RTSP URL like "rtsp://your_camera_ip/stream"
    capture_and_detect(0)  # Change to RTSP URL when you have one