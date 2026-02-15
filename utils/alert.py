# utils/alert.py
import os
import time
import cv2

# Optional sound via pygame
try:
    import pygame
    _PG_OK = True # type: ignore
except Exception:
    _PG_OK = False
    pygame = None


_ALERT_SOUND = os.path.join("static", "alert.mp3")
_ALERT_IMG_DIR = os.path.join("logs", "alerts")
os.makedirs(_ALERT_IMG_DIR, exist_ok=True)


def _play_sound():
    if not _PG_OK:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        if os.path.exists(_ALERT_SOUND):
            snd = pygame.mixer.Sound(_ALERT_SOUND)
            snd.play()
    except Exception as e:
        print("[WARNING] Could not play alert sound:", e)


def trigger_alert(user_id: str, frame_bgr):
    """
    Plays a sound (if available) and saves a snapshot into logs/alerts/.
    """
    try:
        ts = time.strftime("%Y%m%d-%H%M%S")
        fname = f"alert_{user_id}_{ts}.jpg"
        path = os.path.join(_ALERT_IMG_DIR, fname)
        if frame_bgr is not None:
            cv2.imwrite(path, frame_bgr)
    except Exception as e:
        print("[WARNING] Failed to save alert snapshot:", e)

    _play_sound()
