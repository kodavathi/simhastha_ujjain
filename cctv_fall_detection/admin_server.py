from flask import Flask, request, render_template, send_from_directory, jsonify
import os
from datetime import datetime
import cv2
import numpy as np

app = Flask(__name__)
ALERTS = []
live_frame = None  # latest frame for UI

SNAPSHOT_DIR = "fall_snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


@app.route('/')
def dashboard():
    return render_template('dashboard.html', alerts=ALERTS)


# Receive live frame (JPEG bytes)
@app.route('/frame', methods=['POST'])
def receive_frame():
    global live_frame
    if request.data:
        np_arr = np.frombuffer(request.data, np.uint8)
        live_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if live_frame is not None:
            cv2.imwrite(os.path.join(SNAPSHOT_DIR, "latest.jpg"), live_frame)
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "no data"}), 400


@app.route('/alert', methods=['POST'])
def receive_alert():
    person_id = request.form.get("person_id")
    location = request.form.get("location")
    note = request.form.get("note", "")
    snapshot = request.files.get("snapshot_image")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = None
    if snapshot:
        filename = f"fall_{person_id}_{timestamp}.jpg"
        snapshot.save(os.path.join(SNAPSHOT_DIR, filename))

    ALERTS.append({
        "person_id": person_id,
        "timestamp": timestamp,
        "location": location,
        "note": note,
        "snapshot": filename
    })
    return jsonify({"status": "alert received"}), 200


@app.route('/snapshots/<filename>')
def serve_snapshot(filename):
    return send_from_directory(SNAPSHOT_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
