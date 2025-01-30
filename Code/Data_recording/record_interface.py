import cv2
import time

# Initialize camera
cap = cv2.VideoCapture(0)

# Define codec
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None
recording = False

print("Press 'r' to start recording, 's' to stop, and 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow('Video Feed', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('r') and not recording:
        filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}.avi"
        print(f"Recording started: {filename}")
        out = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        recording = True

    if key == ord('s') and recording:
        print("Recording stopped.")
        recording = False
        out.release()
        out = None

    if recording and out is not None:
        out.write(frame)

    if key == ord('q'):  # Press 'q' to exit
        break

# Cleanup
cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
