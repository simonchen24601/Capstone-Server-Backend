from flask import Flask, request, jsonify, send_file
import io
from flask_cors import CORS
from config import Config
from models import db, TemperatureData, LogData, ScreenShotData, APIKey
from auth import require_api_key
import secrets

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)

# create tables if not exist
with app.app_context():
    db.create_all()

# ---- Simple request/response logging ----
# @app.before_request
# def log_request_payload():
#     print(f"[REQ] {request.method} {request.path} ")

# @app.after_request
# def log_response_payload(response):
#     print(f"[RES] {request.method} {request.path} status={response.status_code}")
#     return response

# ---- Admin endpoint to generate API keys ----
@app.route('/create_api_key', methods=['POST'])
def create_api_key():
    data = request.get_json()
    if "device_name" not in data:
        return jsonify({"error": "device_name required"}), 400

    key = secrets.token_hex(32)  # 64-char key
    new_key = APIKey(key=key, device_name=data["device_name"])
    db.session.add(new_key)
    db.session.commit()

    return jsonify({"device_name": data["device_name"], "api_key": key})

@app.route('/', methods=['GET'])
def home():
    return "IOT REST API", 200

# ---- Devices Endpoints ----
@app.route('/devices', methods=['GET'])
@require_api_key
def list_devices():
    # Return unique device names registered via API keys
    names = db.session.query(APIKey.device_name).distinct().order_by(APIKey.device_name.asc()).all()
    return jsonify([n[0] for n in names])

# ---- TemperatureData Endpoints ----
@app.route('/sensor/temperature', methods=['POST'])
@require_api_key
def create_temperature_data():
    data = request.get_json(silent=True) or {}
    required = ["device_id", "temperature_celsius", "humidity_percent"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        temperature = float(data["temperature_celsius"])
        humidity = float(data["humidity_percent"])
    except (TypeError, ValueError):
        return jsonify({"error": "temperature_celsius and humidity_percent must be numbers"}), 400

    record = TemperatureData(
        device_id=data["device_id"],
        temperature_celsius=temperature,
        humidity_percent=humidity
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({
        "id": record.id,
        "device_id": record.device_id,
        "temperature_celsius": record.temperature_celsius,
        "humidity_percent": record.humidity_percent,
        "timestamp": record.timestamp.isoformat() if record.timestamp else None
    }), 201

@app.route('/sensor/temperature', methods=['GET'])
@require_api_key
def list_temperature_data():
    device_id = request.args.get('device_id')
    query = TemperatureData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    results = query.order_by(TemperatureData.id.desc()).limit(100).all()
    return jsonify([
        {
            "id": r.id,
            "device_id": r.device_id,
            "temperature_celsius": r.temperature_celsius,
            "humidity_percent": r.humidity_percent,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None
        } for r in results
    ])

@app.route('/sensor/temperature/<int:record_id>', methods=['GET'])
@require_api_key
def get_temperature_data(record_id: int):
    r = TemperatureData.query.get(record_id)
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": r.id,
        "device_id": r.device_id,
        "temperature_celsius": r.temperature_celsius,
        "humidity_percent": r.humidity_percent,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None
    })

@app.route('/sensor/temperature/latest', methods=['GET'])
@require_api_key
def get_latest_temperature_data():
    device_id = request.args.get('device_id')
    query = TemperatureData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    r = query.order_by(TemperatureData.id.desc()).first()
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": r.id,
        "device_id": r.device_id,
        "temperature_celsius": r.temperature_celsius,
        "humidity_percent": r.humidity_percent,
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

@app.route('/logs/latest', methods=['GET'])
@require_api_key
def get_latest_log():
    device_id = request.args.get('device_id')
    query = LogData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    r = query.order_by(LogData.id.desc()).first()
    if not r:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": r.id,
        "device_id": r.device_id,
        "message": r.message,
        "timestamp": r.timestamp.isoformat() if r.timestamp else None
    })

# ---- ScreenShotData Endpoints ----
@app.route('/sensor/screenshot', methods=['POST'])
@require_api_key
def create_screenshot():
    # Expect multipart/form-data with fields: device_id, format, image (file)
    device_id = request.form.get('device_id')
    img_format = request.form.get('format')
    image = request.files.get('image')
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    if not img_format:
        return jsonify({"error": "format required (e.g., 'png', 'jpg')"}), 400
    if image is None:
        return jsonify({"error": "image file required (form field 'image')"}), 400

    data = image.read()
    if not data:
        return jsonify({"error": "empty image data"}), 400

    record = ScreenShotData(device_id=device_id, format=img_format, image_data=data)
    db.session.add(record)
    db.session.commit()
    return jsonify({
        "id": record.id,
        "device_id": record.device_id,
        "format": record.format,
        "size_bytes": len(data),
        "timestamp": record.timestamp.isoformat() if record.timestamp else None
    }), 201

@app.route('/sensor/screenshot', methods=['GET'])
@require_api_key
def list_screenshots():
    device_id = request.args.get('device_id')
    query = ScreenShotData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    results = query.order_by(ScreenShotData.id.desc()).limit(100).all()
    return jsonify([
        {
            "id": r.id,
            "device_id": r.device_id,
            "format": r.format,
            "size_bytes": len(r.image_data) if r.image_data else 0,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None
        } for r in results
    ])

@app.route('/sensor/screenshot/<int:record_id>', methods=['GET'])
@require_api_key
def get_screenshot(record_id: int):
    r = ScreenShotData.query.get(record_id)
    if not r:
        return jsonify({"error": "Not found"}), 404
    # Return raw image bytes; infer simple mime from stored format
    fmt = (r.format or 'bin').lower()
    mime = 'application/octet-stream'
    if fmt in ('png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'):
        if fmt == 'jpg':
            fmt = 'jpeg'
        mime = f'image/{fmt}'
    return send_file(
        io.BytesIO(r.image_data),
        mimetype=mime,
        as_attachment=False,
        download_name=f"screenshot_{record_id}.{r.format or 'bin'}"
    )

@app.route('/sensor/screenshot/latest', methods=['GET'])
@require_api_key
def get_latest_screenshot():
    device_id = request.args.get('device_id')
    query = ScreenShotData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    r = query.order_by(ScreenShotData.id.desc()).first()
    if not r:
        return jsonify({"error": "Not found"}), 404
    fmt = (r.format or 'bin').lower()
    mime = 'application/octet-stream'
    if fmt in ('png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'):
        if fmt == 'jpg':
            fmt = 'jpeg'
        mime = f'image/{fmt}'
    return send_file(
        io.BytesIO(r.image_data),
        mimetype=mime,
        as_attachment=False,
        download_name=f"screenshot_latest.{r.format or 'bin'}"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
