# utils/detector.py
import os
import cv2
import numpy as np

# YOLO is optional. If not available or model missing, we fall back to motion detection.
try:
    from ultralytics import YOLO
    _ULTRALYTICS_OK = True
except Exception:
    YOLO = None
    _ULTRALYTICS_OK = False


# Cache for loaded YOLO models
_LOADED_MODELS = {}


def get_model_for_role(role: str):
    """
    Maps user role -> model path. Place your .pt files in models/ if you have them.
    If no model exists for a role, app will still run using motion detection fallback.
    """
    mp = {
        "home": "models/home_model.pt",
        "defence": "models/defence_model.pt",
        "farm": "models/farm_model.pt",
    }
    return mp.get(role)


def _safe_path_isempty(path) -> bool:
    # Make sure we don't try truthiness on numpy arrays, etc.
    return path is None or (isinstance(path, str) and path.strip() == "")


def load_model(path: str):
    """
    Loads and caches a YOLO model if available and the file exists.
    Returns the model or None.
    """
    if _safe_path_isempty(path):
        return None
    if not _ULTRALYTICS_OK:
        return None
    if path in _LOADED_MODELS:
        return _LOADED_MODELS[path]
    if os.path.exists(path):
        try:
            model = YOLO(path)
            _LOADED_MODELS[path] = model
            return model
        except Exception as e:
            print("[WARNING] Failed to load YOLO model:", e)
    return None


def detect_frame(model_path: str, frame: np.ndarray):
    """
    Runs detection and returns:
        (anomaly_flag: bool, annotated_frame: np.ndarray)

    Logic:
      - If a YOLO model is available, we mark anomaly=True when any object is detected.
      - Otherwise we use simple motion detection via MOG2 background subtractor.
    """
    annotated = frame.copy()
    model = load_model(model_path)

    # YOLO path
    if model is not None:
        anomaly = False
        try:
            results = model(annotated, imgsz=640, verbose=False)
            for r in results:
                boxes = getattr(r, "boxes", None)
                names = getattr(r, "names", {})
                if boxes is None:
                    continue
                for box in boxes:
                    # xyxy -> [x1,y1,x2,y2]
                    xyxy = box.xyxy.cpu().numpy()[0].astype(int)
                    x1, y1, x2, y2 = xyxy.tolist()
                    cls_id = int(box.cls.cpu().numpy()[0])
                    conf = float(box.conf.cpu().numpy()[0])
                    label = f"{names.get(cls_id, str(cls_id))} {conf:.2f}"

                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(
                        annotated,
                        label,
                        (x1, max(10, y1 - 7)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA,
                    )
                    anomaly = True
        except Exception as e:
            print("[WARNING] YOLO inference failed, fallback to motion. Error:", e)
            model = None  # fall through to motion below

        return anomaly, annotated

    # Fallback motion detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if not hasattr(detect_frame, "_fgbg"):
        detect_frame._fgbg = cv2.createBackgroundSubtractorMOG2(history=120, varThreshold=32, detectShadows=False)
    fgmask = detect_frame._fgbg.apply(gray)

    # Clean mask
    fgmask = cv2.medianBlur(fgmask, 5)
    _, fgmask = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    anomaly = False
    for c in contours:
        if cv2.contourArea(c) > 800:  # tune threshold if needed
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            anomaly = True

    return anomaly, annotated
