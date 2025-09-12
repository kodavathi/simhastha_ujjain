# Simhastha Ujjain – Intelligent CCTV Monitoring System

An **AI/ML-powered CCTV monitoring and analysis platform** designed for large gatherings such as the **Simhastha Ujjain Kumbh Mela**.  
The system leverages **computer vision, deep learning, and real-time video analytics** to detect critical events such as **falls, disasters, crowd congestion, SOS situations, and lost-and-found cases**, ensuring better safety and management of mass gatherings.

---

## 📑 Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## 🏗 Introduction
Mass gatherings like **Simhastha Ujjain** attract millions of people, creating challenges in **safety, crowd control, and emergency response**.  
This project uses **CCTV cameras integrated with AI models** to provide **real-time monitoring and analytics**, enabling authorities to **detect incidents faster and respond more effectively**.

---

## ✨ Features
- ✅ **Fall Detection** – Real-time detection of falls using YOLOv8 pose estimation.  
- ✅ **SOS Triggering** – Immediate alerts when emergencies are detected.  
- ✅ **Disaster Detection & Analysis** – AI-powered analysis of unusual crowd patterns.  
- ✅ **Crowd Flow Monitoring** – Tracking congestion, density, and movement direction.  
- ✅ **Lost & Found Support** – Helps identify missing persons in CCTV feeds.  
- ✅ **Web Dashboard (Streamlit + HTML templates)** – Visualization of events and alerts.  
- ✅ **Logging & Reports** – Generates detection logs, accuracy reports, and alerts.  

---

## 🛠 Tech Stack
- **Programming Language:** Python 3.10+  
- **Machine Learning & Computer Vision:**  
  - YOLOv8 (object detection & pose estimation)  
  - OpenCV  
  - NumPy / Pandas  
  - Scikit-learn  
- **Deep Learning Frameworks:**  
  - PyTorch  
- **Web & Visualization:**  
  - Streamlit  
  - Flask / HTML / JS / CSS  
- **Others:**  
  - Logging & alerting utilities  
  - Custom heuristics for fall detection  

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/kodavathi/simhastha_ujjain.git
cd simhastha_ujjain/cctv_fall_detection
2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

3. Install Dependencies
pip install -r requirements.txt

🚀 Usage
1. Run the AI Engine
python run_engine.py

2. Start the Admin Server (Dashboard)
python admin_server.py

3. Access the Dashboard

Open browser and navigate to:

http://localhost:5000

4. Streamlit Interface (optional)
streamlit run app.py

🔧 Configuration

Model Weights:

Pretrained YOLOv8 weights (yolov8n.pt, yolov8n-pose.pt) included.

Thresholds & Heuristics:

Configurable in fall_heuristic.py.

Alert Settings:

Modify alert_client.py for custom SOS triggers (e.g., SMS, email, sirens).

📊 Examples

Fall detection snapshots saved in:

cctv_fall_detection/fall_snapshots/


Accuracy calculations:

python calculate_accuracy.py


Logs of detections:

cctv_fall_detection/detections.log

🐞 Troubleshooting

Models not found: Ensure yolov8n.pt and yolov8n-pose.pt are in cctv_fall_detection/.

CUDA/CPU issues: Verify PyTorch is installed with correct GPU support.

Web dashboard not loading: Check that Flask or Streamlit server is running without errors.

Accuracy mismatch: Ensure ground_truth.csv is properly formatted.
