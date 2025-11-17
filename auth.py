from flask import request, jsonify
from functools import wraps
from models import APIKey

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return jsonify({"error": "API key missing"}), 401

        key_obj = APIKey.query.filter_by(key=api_key).first()
        if not key_obj:
            return jsonify({"error": "Invalid API key"}), 403

        return f(*args, **kwargs)

    return decorated