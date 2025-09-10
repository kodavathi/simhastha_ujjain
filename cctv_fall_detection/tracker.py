# app/tracker.py
import numpy as np

def iou(boxA, boxB):
    """Compute Intersection over Union between two boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0]+boxA[2], boxB[0]+boxB[2])
    yB = min(boxA[1]+boxA[3], boxB[1]+boxB[3])

    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH

    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    return interArea / float(boxAArea + boxBArea - interArea + 1e-5)

class Tracker:
    def __init__(self, iou_threshold=0.3):
        self.next_id = 1
        self.objects = {}  # id -> bbox
        self.iou_threshold = iou_threshold

    def update(self, detections):
        """
        Assign IDs to detected people based on IoU with previous bboxes.
        detections: [{'id': None, 'bbox': (x,y,w,h)}, ...]
        Returns tracked objects with IDs assigned
        """
        updated = []

        assigned_ids = set()
        for det in detections:
            bbox = det['bbox']
            best_id = None
            best_iou = 0
            for obj_id, obj_bbox in self.objects.items():
                if obj_id in assigned_ids:
                    continue
                score = iou(bbox, obj_bbox)
                if score > best_iou:
                    best_iou = score
                    best_id = obj_id

            if best_iou > self.iou_threshold:
                det['id'] = best_id
                self.objects[best_id] = bbox
                assigned_ids.add(best_id)
            else:
                det['id'] = self.next_id
                self.objects[self.next_id] = bbox
                assigned_ids.add(self.next_id)
                self.next_id += 1

            updated.append(det)

        # Remove lost objects
        current_ids = [d['id'] for d in updated]
        lost_ids = set(self.objects.keys()) - set(current_ids)
        for lid in lost_ids:
            del self.objects[lid]

        return updated
