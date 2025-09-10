# pose_estimator.py
import cv2
import numpy as np

class PoseEstimator:
    def __init__(self, model_path="pose_model.tflite"):
        """
        Initialize the pose estimator.
        You can replace this with your TFLite/MediaPipe/Ultralytics pose model.
        """
        self.model_path = model_path
        # Example: if using MediaPipe
        try:
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose_model = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        except ImportError:
            print("Mediapipe not installed. Install with `pip install mediapipe`")
            self.pose_model = None

    def estimate(self, frame, tracked):
        """
        Estimate poses for tracked people in the frame.
        Args:
            frame: full frame from the camera
            tracked: list of tracked people dicts [{ 'id': 1, 'bbox': (x,y,w,h) }, ...]
        Returns:
            poses: dictionary { person_id: keypoints_dict }
                   keypoints_dict = { 'left_shoulder': (x,y), 'right_shoulder': (x,y), ... }
        """
        poses = {}
        for person in tracked:
            person_id = person['id']
            bbox = person['bbox']  # (x, y, w, h)
            x, y, w, h = bbox
            cropped = frame[y:y+h, x:x+w].copy()
            keypoints = self._estimate_pose_in_bbox(cropped, x, y)
            poses[person_id] = keypoints
        return poses

    def _estimate_pose_in_bbox(self, crop_frame, x_offset=0, y_offset=0):
        """
        Run pose estimation on cropped person frame.
        Returns keypoints dictionary with coordinates relative to full frame.
        """
        keypoints = {}
        if self.pose_model is None:
            # Dummy keypoints for testing
            keypoints = {
                "left_shoulder": (x_offset + 10, y_offset + 20),
                "right_shoulder": (x_offset + 30, y_offset + 20),
                "left_hip": (x_offset + 12, y_offset + 50),
                "right_hip": (x_offset + 28, y_offset + 50),
            }
            return keypoints

        # Use MediaPipe to estimate pose
        import mediapipe as mp
        import cv2

        crop_rgb = cv2.cvtColor(crop_frame, cv2.COLOR_BGR2RGB)
        results = self.pose_model.process(crop_rgb)

        if results.pose_landmarks:
            h, w, _ = crop_frame.shape
            # Map MediaPipe landmarks to a simple dictionary
            mp_landmarks = results.pose_landmarks.landmark
            keypoints_map = {
                "left_shoulder": mp_landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER],
                "right_shoulder": mp_landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER],
                "left_hip": mp_landmarks[self.mp_pose.PoseLandmark.LEFT_HIP],
                "right_hip": mp_landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP],
            }
            for k, lm in keypoints_map.items():
                keypoints[k] = (int(lm.x * w) + x_offset, int(lm.y * h) + y_offset)
        return keypoints
