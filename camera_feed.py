import cv2

def capture_stream(source=0):  # Default to webcam (0), but can use RTSP URL
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

        # Show the frame in a window
        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Use webcam (0) for testing, or replace with RTSP URL like "rtsp://your_camera_ip/stream"
    capture_stream(0)  # Change to RTSP URL when you have one