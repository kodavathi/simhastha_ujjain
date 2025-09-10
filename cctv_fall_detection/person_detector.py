# app/person_detector.py

from ultralytics import YOLO
import cv2

class PersonDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        """
        Detect people in the frame.
        Returns a list of dicts: [{'id': None, 'bbox': (x,y,w,h)}, ...]
        """
        results = self.model.predict(frame, verbose=False)[0]
        persons = []
        for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
            if int(cls) == 0:  # class 0 is person
                x1, y1, x2, y2 = map(int, box)
                w = x2 - x1
                h = y2 - y1
                persons.append({'id': None, 'bbox': (x1, y1, w, h)})
        return persons
