from flask import Flask, render_template, jsonify, request
import random
import time
import json
import os
from flask_socketio import SocketIO
import eventlet

# Setup Flask and SocketIO
app = Flask(__name__, static_folder="static", template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

# Path to store flight data history
FLIGHT_HISTORY_FILE = 'flight_data.json'

# Ensure flight data is saved to a file
def save_flight_data(flight_data):
    if not os.path.exists(FLIGHT_HISTORY_FILE):
        with open(FLIGHT_HISTORY_FILE, 'w') as f:
            json.dump([], f)  # Initialize the file with an empty list

    with open(FLIGHT_HISTORY_FILE, 'r') as f:
        flight_history = json.load(f)

    # Append the new flight data
    flight_history.append(flight_data)

    # Save the updated flight history
    with open(FLIGHT_HISTORY_FILE, 'w') as f:
        json.dump(flight_history, f)

# Load the flight history from the file
def load_flight_history():
    if not os.path.exists(FLIGHT_HISTORY_FILE):
        return []  # No history available
    with open(FLIGHT_HISTORY_FILE, 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index2.html')  # Serve the frontend HTML

@app.route('/live-data', methods=['GET'])
def live_data():
    # Simulate flight data with random values for testing
    data = {
        "latitude": random.uniform(-90.0, 90.0),
        "longitude": random.uniform(-180.0, 180.0),
        "timestamps": [time.time() - i * 60 for i in range(10)],
        "altitudes": [random.uniform(1000, 20000) for _ in range(10)]
    }

    # Save flight data to file
    save_flight_data(data)

    # Return the simulated live data
    return jsonify(data)

@app.route("/animation-data", methods=['GET'])
def animation_data():
    # Example live telemetry data
    telemetry_data = {
        "rotation": random.uniform(0, 360),  # Rotation in degrees
        "position": {
            "x": random.uniform(-5, 5),
            "y": random.uniform(-5, 5),
            "z": random.uniform(-5, 5)
        },
        "force": {
            "x": random.uniform(0, 10),
            "y": random.uniform(0, 10),
            "z": random.uniform(0, 10)
        }
    }
    return jsonify(telemetry_data)

@app.route('/history', methods=['GET'])
def history():
    # Load and return all flight history data
    flight_history = load_flight_history()
    return jsonify(flight_history)

@app.route('/rockblock/MT', methods=['POST'])
def receive_mt():
    imei = request.args.get('imei')
    username = request.args.get('username')
    password = request.args.get('password')
    data = request.args.get('data')

    # Validate input (simulate simple validation for testing)
    if imei != "300434065264590" or username != "myUser" or password != "myPass":
        return "FAILED,10,Invalid login credentials", 400

    if not data:
        return "FAILED,16,No data", 400

    # Simulate decoding hex data
    try:
        decoded_message = bytes.fromhex(data).decode('utf-8')
    except ValueError:
        return "FAILED,14,Could not decode hex data", 400

    print(f"Received message: {decoded_message}")

    return "OK,4114651"

# Emit live data periodically for testing (optional)
def generate_live_data():
    while True:
        # This is an extra, but could simulate real-time data
        telemetry_data = {
            "rotation": random.uniform(0, 360),  # Rotation in degrees
            "position": {
                "x": random.uniform(-5, 5),
                "y": random.uniform(-5, 5),
                "z": random.uniform(-5, 5)
            }
        }
        socketio.emit("update_telemetry", json.dumps(telemetry_data))
        eventlet.sleep(1)  # Update every second


@socketio.on("connect")
def handle_connect():
    print("Client connected!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

