from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# sensor data

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(32), nullable=False)
    key = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class TemperatureData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    temperature_celsius = db.Column(db.Float, nullable=False)
    humidity_percent = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class ScreenShotData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    format = db.Column(db.String(10), nullable=False)  # e.g., 'png', 'jpg'
    image_data = db.Column(db.LargeBinary, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class LogData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
