# run_engine_safe.py
import cv2
from ultralytics import YOLO
import math
import logging
import os
from collections import defaultdict, deque
from datetime import datetime
from deep_sort_realtime.deepsort_tracker import DeepSort
from alert_client import post_frame_to_dashboard, post_alert_to_dashboard
import requests

# ------------------- CONFIG -------------------
VIDEO_SOURCE = 0  # 0 = webcam, replace with RTSP/HTTP stream
LOG_FILE = "detections.log"
SNAPSHOT_DIR = "fall_snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

ANGLE_THRESHOLD = 30          # degrees
ASPECT_RATIO_THRESHOLD = 1.5  # width / height
DROP_THRESHOLD = 50           # sudden downward motion
HISTORY_LEN = 5
MIN_FRAMES_FOR_ALERT = 2

# ------------------- LOGGING -------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# ------------------- UTILS -------------------
def get_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if dx == 0:
        return 90
    return abs(math.degrees(math.atan2(dy, dx)))


def safe_post_frame(frame):
    try:
        post_frame_to_dashboard(frame)
    except requests.exceptions.RequestException:
        pass  # skip if server is down


def safe_post_alert(person_id, bbox, note, snapshot_image):
    try:
        post_alert_to_dashboard(person_id=person_id, bbox=bbox, note=note, snapshot_image=snapshot_image)
    except requests.exceptions.RequestException:
        pass  # skip if server is down

# ------------------- FALL DETECTOR -------------------
class FallDetector:
    def __init__(self):
        self.prev_positions = defaultdict(lambda: deque(maxlen=HISTORY_LEN))
        self.prev_fall_flags = defaultdict(lambda: deque(maxlen=MIN_FRAMES_FOR_ALERT))
        self.alerted_persons = defaultdict(bool)

    def check_fall(self, person_id, bbox, keypoints):
        x, y, w, h = bbox
        aspect_ratio = w / float(h + 1e-5)

        fall_pose = fall_aspect = fall_motion = False

        # Pose orientation
        required_kps = {"left_shoulder", "right_shoulder", "left_hip", "right_hip"}
        if required_kps.issubset(keypoints.keys()):
            mid_shoulder = (
                (keypoints["left_shoulder"][0] + keypoints["right_shoulder"][0]) / 2,
                (keypoints["left_shoulder"][1] + keypoints["right_shoulder"][1]) / 2
            )
            mid_hip = (
                (keypoints["left_hip"][0] + keypoints["right_hip"][0]) / 2,
                (keypoints["left_hip"][1] + keypoints["right_hip"][1]) / 2
            )
            angle = get_angle(mid_shoulder, mid_hip)
            if angle < ANGLE_THRESHOLD:
                fall_pose = True

        # Aspect ratio
        if aspect_ratio > ASPECT_RATIO_THRESHOLD:
            fall_aspect = True

        # Sudden downward motion
        positions = self.prev_positions[person_id]
        if positions:
            prev_x, prev_y = positions[-1]
            if y - prev_y > DROP_THRESHOLD:
                fall_motion = True
        positions.append((x, y))

        # Combine conditions
        fall_flag = sum([fall_pose, fall_aspect, fall_motion]) >= 2
        self.prev_fall_flags[person_id].append(fall_flag)

        if sum(self.prev_fall_flags[person_id]) >= MIN_FRAMES_FOR_ALERT:
            if not self.alerted_persons[person_id]:
                self.alerted_persons[person_id] = True
                return True
        else:
            self.alerted_persons[person_id] = False

        return False

# ------------------- MAIN -------------------
def main():
    print("[INFO] Loading YOLOv8-pose model...")
    model = YOLO("yolov8n-pose.pt")

    print("[INFO] Starting video stream...")
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print("[ERROR] Cannot access camera/stream")
        return

    fall_detector = FallDetector()
    tracker = DeepSort(max_age=30)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)
        annotated_frame = frame.copy()
        dets = []

        h, w, _ = frame.shape

        for result in results:
            if result.keypoints is None:
                continue

            for i, person in enumerate(result.keypoints.xy):
                person_id = f"{i}"
                try:
                    left_shoulder = person[5].tolist()
                    right_shoulder = person[6].tolist()
                    left_hip = person[11].tolist()
                    right_hip = person[12].tolist()

                    # Build bbox
                    x_min = int(min(left_shoulder[0], right_shoulder[0], left_hip[0], right_hip[0]))
                    y_min = int(min(left_shoulder[1], right_shoulder[1], left_hip[1], right_hip[1]))
                    x_max = int(max(left_shoulder[0], right_shoulder[0], left_hip[0], right_hip[0]))
                    y_max = int(max(left_shoulder[1], right_shoulder[1], left_hip[1], right_hip[1]))

                    # Clamp bbox inside frame
                    x_min = max(0, min(x_min, w - 1))
                    y_min = max(0, min(y_min, h - 1))
                    x_max = max(0, min(x_max, w - 1))
                    y_max = max(0, min(y_max, h - 1))

                    if x_max <= x_min or y_max <= y_min:
                        continue  # skip invalid box

                    bbox = (x_min, y_min, x_max - x_min, y_max - y_min)

                    # Valid detection for DeepSORT
                    dets.append([[x_min, y_min, x_max, y_max], 1.0, None])

                    keypoints_dict = {
                        "left_shoulder": left_shoulder,
                        "right_shoulder": right_shoulder,
                        "left_hip": left_hip,
                        "right_hip": right_hip,
                    }

                    if fall_detector.check_fall(person_id, bbox, keypoints_dict):
                        print(f"⚠️ Fall detected! Person {person_id}")
                        logging.warning(f"Fall detected: Person {person_id}")

                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        snap_path = os.path.join(SNAPSHOT_DIR, f"fall_{person_id}_{timestamp}.jpg")
                        cv2.imwrite(snap_path, frame)

                        safe_post_alert(person_id, bbox, "Fall detected", frame)

                        cv2.putText(annotated_frame, "FALL ALERT!", (20, 40),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

                except Exception as e:
                    print(f"[WARN] Error processing person {i}: {e}")
                    continue

        # Overlay keypoints/pose
        if results:
            annotated_frame = results[0].plot()

        # DeepSORT tracking (safe)
        tracks = []
        if dets:
            try:
                tracks = tracker.update_tracks(dets, frame=frame)
            except Exception as e:
                print(f"[ERROR] DeepSORT failed: {e}")
                tracks = []

        for t in tracks:
            if t.is_confirmed():
                tid = t.track_id
                l, t_, r, b = t.to_ltrb()
                cv2.rectangle(annotated_frame, (int(l), int(t_)), (int(r), int(b)), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"ID: {tid}", (int(l), int(t_)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Dashboard + snapshot
        safe_post_frame(annotated_frame)
        cv2.imwrite(os.path.join(SNAPSHOT_DIR, "latest.jpg"), annotated_frame)

        # Show
        cv2.imshow("CCTV Fall Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] CCTV engine stopped.")


if __name__ == "__main__":
    main()
