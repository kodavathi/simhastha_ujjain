import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

st.set_page_config(page_title="Disaster Management Dashboard", layout="wide")

# Custom CSS for warm color scheme and styling
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #efb2a3 0%, #e07b5a 100%);
    color: #4a2c2a;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(224, 123, 90, 0.6);
    text-align: center;
    font-weight: 600;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.metric-card-alt {
    background: linear-gradient(135deg, #f9d86e 0%, #d4a90d 100%);
    color: #4a3b00;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(212, 169, 13, 0.6);
    text-align: center;
    font-weight: 600;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.metric-card-crowd {
    background: linear-gradient(135deg, #90ccbc 0%, #388083 100%);
    color: #0e2d2f;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(56, 128, 131, 0.6);
    text-align: center;
    font-weight: 600;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.metric-card-fire-high {
    background: linear-gradient(135deg, #d8641a 0%, #b53e0a 100%);
    color: #fceddf;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(181, 62, 10, 0.8);
    text-align: center;
    font-weight: 700;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.metric-card-fire-low {
    background: linear-gradient(135deg, #a7c796 0%, #6c8054 100%);
    color: #f5f9f1;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(108, 128, 84, 0.7);
    text-align: center;
    font-weight: 700;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.alert-info {
    background: linear-gradient(135deg, #fceabb 0%, #f8b500 100%);
    color: #5a3e00;
    padding: 15px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 10px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.alert-box {
    background: linear-gradient(135deg, #d8641a 0%, #b53e0a 100%);
    color: #fceddf;
    padding: 15px;
    border-radius: 12px;
    font-weight: 700;
    margin-bottom: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.success-box {
    background: linear-gradient(135deg, #a7c796 0%, #6c8054 100%);
    color: #f5f9f1;
    padding: 15px;
    border-radius: 12px;
    font-weight: 600;
    margin-top: 10px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.incident-log {
    background: linear-gradient(135deg, #fbe8a6 0%, #f8b500 100%);
    color: #4d3900;
    padding: 15px;
    border-radius: 12px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-height: 200px;
    overflow-y: auto;
    margin-bottom: 15px;
}
.response-status {
    background: linear-gradient(135deg, #d4a90d 0%, #a87700 100%);
    color: white;
    padding: 12px;
    border-radius: 12px;
    font-weight: 600;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("🔥 Simahastha Ujjain Disaster Management Dashboard")
st.markdown("Monitor security, surveillance, and fire risk with AI-powered alerts")

# Load synthetic data
data = pd.read_csv("synthetic_data.csv", parse_dates=["timestamp"])

# Metric Cards Section
col1, col2, col3, col4 = st.columns(4)
col1.markdown(
    f'<div class="metric-card"><h3>Temp (°C)</h3><h1>{data["temperature"].iloc[-1]}</h1></div>',
    unsafe_allow_html=True,
)
col2.markdown(
    f'<div class="metric-card-alt"><h3>Humidity (%)</h3><h1>{data["humidity"].iloc[-1]}</h1></div>',
    unsafe_allow_html=True,
)
col3.markdown(
    f'<div class="metric-card-crowd"><h3>Crowd Density</h3><h1>{data["crowd_density"].iloc[-1]}</h1></div>',
    unsafe_allow_html=True,
)
if data["fire_risk"].iloc[-1] == 1:
    col4.markdown(
        f'<div class="metric-card-fire-high"><h3>Fire Risk</h3><h1>High</h1></div>',
        unsafe_allow_html=True,
    )
else:
    col4.markdown(
        f'<div class="metric-card-fire-low"><h3>Fire Risk</h3><h1>Low</h1></div>',
        unsafe_allow_html=True,
    )

# Climate and Crowd Trends Live Simulation Chart
st.subheader("Climate and Crowd Trends (Live Simulation)")
chart_placeholder = st.empty()
window_size = 4
delay_seconds = 10

for i in range(len(data) - window_size + 1):
    current_data = data.iloc[i : i + window_size]
    chart_placeholder.line_chart(
        current_data.set_index("timestamp")[["temperature", "humidity", "crowd_density"]]
    )
    if i < len(data) - window_size:
        time.sleep(delay_seconds)

# Alert Messages Moved Below the Chart

# Alert info message with warmer gradient
st.markdown(
    '<div class="alert-info">⚠️ Alert has been given to crowd management control and required action will be taken.</div>',
    unsafe_allow_html=True,
)

# Disaster risk detection message below
fire_anomaly = data[data["fire_risk"] == 1]
if not fire_anomaly.empty:
    st.markdown(
        '<div class="alert-box">🔥 Disaster Risk Detected!</div>', unsafe_allow_html=True
    )
else:
    st.markdown(
        '<div class="success-box">✅ No disaster risk detected at the moment.</div>',
        unsafe_allow_html=True,
    )

# Incident History Log feature showing last 5 alerts (synthetic example)
st.subheader("Incident History Log")
incident_logs = [
    {"time": "2025-09-10 09:00", "alert": "Temperature spike detected."},
    {"time": "2025-09-10 10:00", "alert": "Fire risk level high."},
    {"time": "2025-09-10 13:00", "alert": "Crowd density above threshold."},
]
log_messages = "\n".join(
    [f"{item['time']}: {item['alert']}" for item in incident_logs]
)
st.markdown(f'<div class="incident-log"><pre>{log_messages}</pre></div>', unsafe_allow_html=True)

# Response Status Tracker simulation
st.subheader("Response Status Tracker")
st.markdown(
    '<div class="response-status">Current Response: <b>In Progress</b> ⏳</div>',
    unsafe_allow_html=True,
)

# Acknowledge Alert button and message
if st.button("Acknowledge Alert"):
    st.success("Response has been initiated.")

st.sidebar.title("Disaster Management Tools")
st.sidebar.markdown("- Live Metrics\n- Anomaly Detection\n- Crowd Control\n- Alerts Panel")
