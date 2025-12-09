# Capstone Server Backend API

This Flask-based REST API stores IoT sensor readings and device logs.

## Authentication
- Header: `X-API-Key: <api_key>` required for all non-root endpoints.
- Generate keys using `POST /create_api_key`.

## Base
- `GET /` — health check returns `"IOT REST API"`.

## API Keys
- `POST /create_api_key`
	- Body: `{ "device_id": "dev-1" }`
	- 201 Response: `{ "device_id": "dev-1", "api_key": "<64-hex>" }`

## Sensor Data
- `POST /sensor-data`
	- Headers: `X-API-Key`
	- Body: `{ "device_id": "dev-1", "sensor_type": "temp", "value": 22.5 }`
	- 201 Response:
		```json
		{
			"id": 1,
			"device_id": "dev-1",
			"sensor_type": "temp",
			"value": 22.5,
			"timestamp": "2025-12-08T12:34:56+00:00"
		}
		```
- `GET /sensor-data`
	- Headers: `X-API-Key`
	- Query: `device_id`, `sensor_type` (optional)
	- 200 Response: array of latest 100 records.
- `GET /sensor-data/{id}`
	- Headers: `X-API-Key`
	- 200 Response: single record or `404` if not found.

## Logs
- `POST /logs`
	- Headers: `X-API-Key`
	- Body: `{ "device_id": "dev-1", "message": "boot complete" }`
	- 201 Response:
		```json
		{
			"id": 1,
			"device_id": "dev-1",
			"message": "boot complete",
			"timestamp": "2025-12-08T12:34:56+00:00"
		}
		```
- `GET /logs`
	- Headers: `X-API-Key`
	- Query: `device_id` (optional)
	- 200 Response: array of latest 200 logs.
- `GET /logs/{id}`
	- Headers: `X-API-Key`
	- 200 Response: single log or `404`.

## Error Responses
- 400: missing fields or invalid types, e.g. `{ "error": "Missing fields: device_id" }`.
- 404: resource not found, e.g. `{ "error": "Not found" }`.
- 401/403: unauthorized when API key is invalid (from `require_api_key`).

## Run Locally
```bash
python main.py
```

## Examples
```bash
# Create API key
curl -X POST http://localhost:5000/create_api_key \
	-H "Content-Type: application/json" \
	-d '{"device_id":"dev-1"}'

# Create sensor data
curl -X POST http://localhost:5000/sensor-data \
	-H "Content-Type: application/json" \
	-H "X-API-Key: <api_key>" \
	-d '{"device_id":"dev-1","sensor_type":"temp","value":22.5}'

# List sensor data
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/sensor-data?device_id=dev-1&sensor_type=temp"

# Create log
curl -X POST http://localhost:5000/logs \
	-H "Content-Type: application/json" \
	-H "X-API-Key: <api_key>" \
	-d '{"device_id":"dev-1","message":"boot complete"}'

# List logs
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/logs?device_id=dev-1"
```
