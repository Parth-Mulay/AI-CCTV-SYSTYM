# utils/face_watchlist.py
import os
import cv2
import numpy as np

# face_recognition is optional; we degrade gracefully if it's not present
try:
    import face_recognition
    _FR_OK = True
except ImportError as e:
    face_recognition = None
    _FR_OK = False
    print("[WARNING] face_recognition not available:", e)


def load_watchlist_encodings(folder_path: str):
    """
    Scans a folder for images, builds and returns a list of face encodings.
    Returns [] if no faces found or face_recognition not available.
    """
    if not _FR_OK:
        return []

    encodings = []
    # Accept common image formats
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    if not os.path.exists(folder_path):
        return []

    for name in os.listdir(folder_path):
        p = os.path.join(folder_path, name)
        if not os.path.isfile(p):
            continue
        _, ext = os.path.splitext(name.lower())
        if ext not in exts:
            continue
        try:
            img = face_recognition.load_image_file(p)
            faces = face_recognition.face_encodings(img)
            if len(faces) > 0:
                encodings.append(faces[0])
        except Exception as e:
            print(f"[WARNING] Failed to process watchlist image {name}: {e}")

    return encodings


def check_face_watchlist(frame_bgr, watchlist_encodings):
    """
    Returns True if any face in `frame_bgr` matches any encoding in `watchlist_encodings`.
    Returns False when no library or no matches.
    """
    if not _FR_OK:
        return False
    if not watchlist_encodings:
        return False

    # Convert BGR (OpenCV) to RGB for face_recognition
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model="hog")  # fast; switch to 'cnn' if GPU available
    if not boxes:
        return False

    encs = face_recognition.face_encodings(rgb, boxes)
    for enc in encs:
        # compare_faces expects a list of encoding vectors (numpy arrays)
        matches = face_recognition.compare_faces(watchlist_encodings, enc, tolerance=0.6)
        if any(matches):
            return True
    return False
