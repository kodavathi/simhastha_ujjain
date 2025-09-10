import cv2

def draw_bbox(frame, bbox, person_id, fall_detected=False):
    x, y, w, h = bbox
    color = (0, 255, 0) if not fall_detected else (0, 0, 255)
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

    label = f"ID {person_id}"
    if fall_detected:
        label += " FALL ALERT!"
    cv2.putText(frame, label, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame
