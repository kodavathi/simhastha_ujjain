import requests
import cv2

# Flask dashboard base URL
DASHBOARD_URL = "http://127.0.0.1:5000"


def post_frame_to_dashboard(frame):
    """
    Sends a single frame (JPEG raw bytes) to the Flask dashboard.
    """
    try:
        _, jpeg = cv2.imencode('.jpg', frame)

        requests.post(
            f"{DASHBOARD_URL}/frame",
            data=jpeg.tobytes(),
            headers={"Content-Type": "application/octet-stream"},
            timeout=0.5
        )
    except Exception as e:
        print(f"[WARN] Failed to post frame: {e}")


def post_alert_to_dashboard(person_id, bbox, note, snapshot_image=None):
    """
    Sends a fall alert with optional snapshot and location to the dashboard.
    """
    try:
        # bbox = (x, y, w, h) → center = (x + w/2, y + h/2)
        center_x = bbox[0] + bbox[2] // 2
        center_y = bbox[1] + bbox[3] // 2
        location = f"({center_x}, {center_y})"

        data = {
            "person_id": str(person_id),
            "bbox": str(bbox),
            "note": note,
            "location": location,
        }

        files = {}
        if snapshot_image is not None:
            _, jpeg = cv2.imencode('.jpg', snapshot_image)
            files["snapshot_image"] = ("snapshot.jpg", jpeg.tobytes(), "image/jpeg")

        requests.post(
            f"{DASHBOARD_URL}/alert",
            data=data,
            files=files,
            timeout=0.5
        )
        print(f"[INFO] Alert posted for Person {person_id} at {location}")
    except Exception as e:
        print(f"[ERROR] Failed to post alert: {e}")
