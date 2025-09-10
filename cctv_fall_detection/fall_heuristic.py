#fall_heuristic
import numpy as np
from collections import defaultdict, deque

class FallHeuristic:
    def __init__(self, history_len=10, min_frames_for_fall=2):
        """
        history_len: number of previous positions to track per person
        min_frames_for_fall: minimum frames the conditions must persist to trigger fall
        """
        self.person_features = defaultdict(lambda: deque(maxlen=history_len))
        self.prev_fall_flags = defaultdict(lambda: deque(maxlen=min_frames_for_fall))

    def get_angle(self, a, b):
        """Compute angle between two points (mid-shoulder to mid-hip)."""
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        angle = np.degrees(np.arctan2(dy, dx))
        return abs(angle)

    def is_fall(self, person_id, bbox, keypoints):
        """
        Multi-factor fall detection using last N frames.
        Returns True if fall detected.
        """
        x, y, w, h = bbox
        aspect_ratio = w / float(h + 1e-5)

        # Pose orientation
        fall_pose = False
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
            angle = self.get_angle(mid_shoulder, mid_hip)
            if angle < 40:  # horizontal
                fall_pose = True

        # Bounding box aspect ratio
        fall_aspect = aspect_ratio > 1.5

        # Vertical velocity
        prev_positions = self.person_features[person_id]
        if prev_positions:
            _, prev_y, _, prev_h, _ = prev_positions[-1]
            dy = y - prev_y
            fall_motion = dy > prev_h * 0.5  # sudden drop
        else:
            fall_motion = False

        # Store current frame feature
        self.person_features[person_id].append((x, y, w, h, fall_pose, fall_aspect, fall_motion))

        # Compute confidence over history
        history_flags = [fp or fa or fm for _, _, _, _, fp, fa, fm in self.person_features[person_id]]
        fall_confidence = sum(history_flags)

        # Persist fall detection
        fall_flag = sum([fall_pose, fall_aspect, fall_motion]) >= 2
        self.prev_fall_flags[person_id].append(fall_flag)
        if sum(self.prev_fall_flags[person_id]) >= 2:
            return True
        return False
