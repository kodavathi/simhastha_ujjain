# simhastha_ujjain  
# Crowd Flow Alert System – Ujjain Hackathon

## Overview
Real-time volunteer tracking for crowd safety. Tracks location, logs users, and sends SMS alerts when entering restricted areas.

---

## Files
- `app.py` – Flask backend.  
- `index.html` – Phone-side tracker.

---

## Important: Update Frontend Evrytime to run
In `index.html`, find the line:

```js
fetch('https://YOUR_NGROK_URL/update-location', ...)
Replace https://YOUR_NGROK_URL with your ngrok URL generated after running:

bash
Copy code
ngrok http 5000
