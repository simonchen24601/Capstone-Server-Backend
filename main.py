from flask import Flask, request, jsonify
from config import Config
from models import db, SensorData, APIKey
from auth import require_api_key
import secrets
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# create tables if not exist
with app.app_context():
    db.create_all()

# ---- Admin endpoint to generate API keys ----
@app.route('/create_api_key', methods=['POST'])
def create_api_key():
    data = request.get_json()
    if "device_id" not in data:
        return jsonify({"error": "device_id required"}), 400

    key = secrets.token_hex(32)  # 64-char key
    new_key = APIKey(key=key, device_id=data["device_id"])
    db.session.add(new_key)
    db.session.commit()

    return jsonify({"device_id": data["device_id"], "api_key": key})

@app.route('/', methods=['GET'])
def home():
    return "I am a teapot", 418


# ---- Protected IoT Data Ingest ----
@app.route('/data', methods=['POST'])
@require_api_key
def receive_data():
    data = request.get_json()

    if not data or "device_id" not in data or "sensor_type" not in data or "value" not in data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    entry = SensorData(
        device_id=data["device_id"],
        sensor_type=data["sensor_type"],
        value=float(data["value"])
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({"status": "ok", "message": "Data logged"})

# ---- Protected Command Fetch ----
@app.route('/command', methods=['GET'])
@require_api_key
def get_command():
    command = {
        "action": "set_motor",
        "speed": 120,
        "mode": "auto"
    }
    return jsonify(command)

# Public
@app.route('/logs', methods=['GET'])
def list_logs():
    logs = SensorData.query.order_by(SensorData.timestamp.desc()).limit(20).all()
    return jsonify([
        {
            "id": log.id,
            "device_id": log.device_id,
            "sensor_type": log.sensor_type,
            "value": log.value,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
