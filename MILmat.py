import socket
import cv2
import numpy as np
import sys
import struct
import pickle
import time
import math
host = socket.gethostname()
port = 5000  # initiate port no above 1024
print(host)
c = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    conn,addr = s.accept()
    with conn:

# Create a video capture object
        cap = cv2.VideoCapture(0)

        # Create a MIL object tracker
        tracker = cv2.TrackerMIL_create()

        # Get the first frame
        ret, frame = cap.read()

        # Select the region of interest (ROI) to track
        bbox = cv2.selectROI(frame, False)

        # Initialize the tracker with the ROI
        tracker.init(frame, bbox)

        # Loop through the frames
        while True:
            # Read a frame from the video capture object
            ret, frame = cap.read()

            # Update the tracker with the current frame
            success, bbox = tracker.update(frame)

            # If tracking is successful, draw a bounding box around the tracked object
            if success:
                x, y, w, h = [int(i) for i in bbox]
                time.sleep(0.03)
                bytes_val = x.to_bytes(math.ceil(x/255),'little')
                conn.sendall(bytes_val)
                bytes_val1 = y.to_bytes(math.ceil(y/255),'little')
                conn.sendall(bytes_val1)
                bytes_val2 = w.to_bytes(math.ceil(w/255),'little')
                conn.sendall(bytes_val2)
                bytes_val3 = h.to_bytes(math.ceil(h/255),'little')
                conn.sendall(bytes_val3)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the current frame
            cv2.imshow("MIL Object Tracking", frame)

            # Exit if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture object and close all windows
        conn.close()
        cap.release()
        cv2.destroyAllWindows()
