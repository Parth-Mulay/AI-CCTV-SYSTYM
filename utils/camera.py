import cv2
from utils.motion import MotionDetector
from utils.alert import trigger_alert

class VideoCamera:
    def __init__(self, source=0, model_path=None, user_id=None, watchlist=None):
        self.source = source
        self.model_path = model_path
        self.user_id = user_id
        self.watchlist = watchlist
        self.detector = MotionDetector()

        # Try to open webcam
        self.video = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        if not self.video.isOpened():
            raise RuntimeError(f"Could not open video source: {self.source}")

    def __del__(self):
        if hasattr(self, "video") and self.video.isOpened():
            self.video.release()

    def get_frame_bytes(self, watchlist=None):
        """Return frame capture status, JPEG bytes, anomaly flag, face flag"""
        success, frame = self.video.read()
        if not success:
            return False, None, False, False

        # Motion detection
        anomaly_flag = self.detector.detect(frame)

        # Face detection against watchlist
        face_flag = False
        if watchlist:
            face_flag = self.check_watchlist_faces(frame, watchlist)

        # Trigger alerts if needed
        if anomaly_flag or face_flag:
            trigger_alert(self.user_id, frame)

        _, jpg_bytes = cv2.imencode('.jpg', frame)
        return True, jpg_bytes.tobytes(), anomaly_flag, face_flag

    def check_watchlist_faces(self, frame, watchlist):
        """
        Placeholder for face recognition against watchlist.
        Return True if a match is found.
        """
        # TODO: integrate face recognition logic here
        return False
