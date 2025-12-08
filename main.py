from flask import Flask, request, jsonify
from config import Config
from models import db, SensorData, LogData, APIKey
from auth import require_api_key
import secrets
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# create tables if not exist
with app.app_context():
    db.create_all()

# ---- Simple request/response logging ----
@app.before_request
def log_request_payload():
    try:
        payload = request.get_data(cache=True, as_text=True)
    except Exception:
        payload = "<unreadable>"
    print(f"[REQ] {request.method} {request.path} payload={payload}")

@app.after_request
def log_response_payload(response):
    try:
        body = response.get_data(as_text=True)
    except Exception:
        body = "<unreadable>"
    print(f"[RES] {request.method} {request.path} status={response.status_code} body={body}")
    return response

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
    return "IOT REST API", 200

# ---- SensorData Endpoints ----
@app.route('/sensor-data', methods=['POST'])
@require_api_key
def create_sensor_data():
    data = request.get_json(silent=True) or {}
    required = ["device_id", "sensor_type", "value"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        value = float(data["value"])
    except (TypeError, ValueError):
        return jsonify({"error": "value must be a number"}), 400

    record = SensorData(
        device_id=data["device_id"],
        sensor_type=data["sensor_type"],
        value=value
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({
        "id": record.id,
        "device_id": record.device_id,
        "sensor_type": record.sensor_type,
        "value": record.value,
        "timestamp": record.timestamp.isoformat() if record.timestamp else None
    }), 201

@app.route('/sensor-data', methods=['GET'])
@require_api_key
def list_sensor_data():
    device_id = request.args.get('device_id')
    sensor_type = request.args.get('sensor_type')
    query = SensorData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    if sensor_type:
        query = query.filter_by(sensor_type=sensor_type)
    results = query.order_by(SensorData.id.desc()).limit(100).all()
    return jsonify([
        {
            "id": r.id,
            "device_id": r.device_id,
            "sensor_type": r.sensor_type,
            "value": r.value,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None
        } for r in results
    ])

@app.route('/sensor-data/<int:record_id>', methods=['GET'])
@require_api_key
def get_sensor_data(record_id: int):
    r = SensorData.query.get(record_id)
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": r.id,
        "device_id": r.device_id,
        "sensor_type": r.sensor_type,
        "value": r.value,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None
    })

# ---- LogData Endpoints ----
@app.route('/logs', methods=['POST'])
@require_api_key
def create_log():
    data = request.get_json(silent=True) or {}
    required = ["device_id", "message"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    record = LogData(
        device_id=data["device_id"],
        message=data["message"]
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({
        "id": record.id,
        "device_id": record.device_id,
        "message": record.message,
        "timestamp": record.timestamp.isoformat() if record.timestamp else None
    }), 201

@app.route('/logs', methods=['GET'])
@require_api_key
def list_logs():
    device_id = request.args.get('device_id')
    query = LogData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    results = query.order_by(LogData.id.desc()).limit(200).all()
    return jsonify([
        {
            "id": r.id,
            "device_id": r.device_id,
            "message": r.message,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None
        } for r in results
    ])

@app.route('/logs/<int:record_id>', methods=['GET'])
@require_api_key
def get_log(record_id: int):
    r = LogData.query.get(record_id)
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": r.id,
        "device_id": r.device_id,
        "message": r.message,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
