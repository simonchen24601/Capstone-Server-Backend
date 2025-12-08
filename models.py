from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# sensor data

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(32), nullable=False)
    key = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.timezone.utc)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    sensor_type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.timezone.utc)

class LogData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.timezone.utc)
