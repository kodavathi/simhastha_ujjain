from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from datetime import datetime
import os
from twilio.rest import Client

app = Flask(__name__)
CORS(app)


user_locations = {}
sms_sent_users = set()  


TARGET_REGION = {
    'lat_min': 30.1800,
    'lat_max': 30.1900,
    'long_min': 75.7700,
    'long_max': 75.7800
}

LOG_CSV_FILE = 'user_log.csv'


TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''  

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


if not os.path.exists(LOG_CSV_FILE):
    with open(LOG_CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'name', 'phone_number'])

def is_in_target_region(lat, long):
    return (TARGET_REGION['lat_min'] <= lat <= TARGET_REGION['lat_max'] and
            TARGET_REGION['long_min'] <= long <= TARGET_REGION['long_max'])

def send_sms_alert(phone_number, message):
    """Send SMS using Twilio"""
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent to {phone_number}: SID {message.sid}")
    except Exception as e:
        print(f"Error sending SMS to {phone_number}: {e}")

@app.route('/update-location', methods=['POST'])
def update_location():
    data = request.get_json()
    name = data['name']
    phone_number = data['phone_number']
    latitude = data['latitude']
    longitude = data['longitude']

    if phone_number not in user_locations:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, name, phone_number])

   
    user_locations[phone_number] = {
        'name': name,
        'latitude': latitude,
        'longitude': longitude
    }

    
    if is_in_target_region(latitude, longitude) and phone_number not in sms_sent_users:
        send_sms_alert(phone_number, "ALERT! You are in the restricted region. Please move!")
        sms_sent_users.add(phone_number)

    return 'Location Updated'

@app.route('/get-location', methods=['GET'])
def get_location():
    return jsonify(user_locations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
