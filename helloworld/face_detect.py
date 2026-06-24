"""
OpenCV Real-time Face Detection
================================
Usage: python face_detect.py
Controls: ESC or 'q' to quit
"""

import cv2
import sys
import os


def get_cascade_path():
    """Get the Haar cascade XML file path from the installed opencv-python"""
    cv2_dir = os.path.dirname(cv2.__file__)
    cascade_path = os.path.join(cv2_dir, "data", "haarcascade_frontalface_default.xml")

    if not os.path.exists(cascade_path):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

    if not os.path.exists(cascade_path):
        print("ERROR: cannot find haarcascade_frontalface_default.xml")
        sys.exit(1)

    return cascade_path


def main():
    print("=" * 50)
    print("  OpenCV Real-time Face Detection")
    print("=" * 50)

    # 1. Load Haar cascade classifier
    cascade_path = get_cascade_path()
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("ERROR: failed to load classifier: " + cascade_path)
        sys.exit(1)
    print("[OK] Model loaded: " + os.path.basename(cascade_path))

    # 2. Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: cannot open camera")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("[OK] Camera opened: {}x{} @ {:.0f} FPS".format(width, height, fps))
    print("-" * 50)
    print("Controls: [ESC] or [q] to quit")
    print("-" * 50)

    while True:
        # 3. Read a frame
        ret, frame = cap.read()
        if not ret:
            print("WARNING: failed to read frame")
            break

        # 4. Convert to grayscale (required by Haar cascade)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 5. Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # 6. Draw face rectangles
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame, "Face ({}x{})".format(w, h),
                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 1
            )

        # 7. Overlay info
        info_text = "Faces: {}  |  Press ESC/q to quit".format(len(faces))
        cv2.putText(
            frame, info_text,
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (0, 255, 0), 1
        )

        # 8. Show the frame
        cv2.imshow("Face Detection - OpenCV", frame)

        # 9. Check for quit key
        key = cv2.waitKey(30) & 0xFF
        if key == 27 or key == ord('q'):
            print("\nUser quit")
            break

    # 10. Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Program exited")


if __name__ == "__main__":
    main()
