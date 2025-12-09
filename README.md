# Capstone Server Backend API

This Flask-based REST API stores IoT sensor readings and device logs.

## Authentication
- Header: `X-API-Key: <api_key>` required for all non-root endpoints.
- Generate keys using `POST /create_api_key`.

## Base
- `GET /` — health check returns `"IOT REST API"`.

## Devices
- `GET /devices`
	- Headers: `X-API-Key`
	- 200 Response: array of device names registered via API keys, e.g. `["dev-1", "dev-2"]`.

## API Keys
- `POST /create_api_key`
	- Body: `{ "device_name": "dev-1" }`
	- 201 Response: `{ "device_name": "dev-1", "api_key": "<64-hex>" }`

## Temperature Data
- `POST /temperature`
	- Headers: `X-API-Key`
	- Body: `{ "device_id": "dev-1", "temperature_celsius": 22.5, "humidity_percent": 45.2 }`
	- 201 Response:
		```json
		{
			"id": 1,
			"device_id": "dev-1",
			"temperature_celsius": 22.5,
			"humidity_percent": 45.2,
			"timestamp": "2025-12-08T12:34:56+00:00"
		}
		```
- `GET /temperature`
	- Headers: `X-API-Key`
	- Query: `device_id` (optional)
	- 200 Response: array of latest 100 records.
- `GET /temperature/{id}`
	- Headers: `X-API-Key`
	- 200 Response: single record or `404` if not found.
- `GET /sensor/temperature/latest`
	- Headers: `X-API-Key`
	- Query: `device_id` (optional to get latest for specific device)
	- 200 Response: latest record or `404` if none.

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
- `GET /logs/latest`
	- Headers: `X-API-Key`
	- Query: `device_id` (optional to get latest for specific device)
	- 200 Response: latest log or `404`.

## Screenshots
- `POST /sensor/screenshot`
	- Headers: `X-API-Key`
	- Content-Type: `multipart/form-data`
	- Form fields:
		- `device_id`: string
		- `format`: string (e.g., `png`, `jpg`)
		- `image`: file (binary image data)
	- 201 Response:
		```json
		{
			"id": 1,
			"device_id": "dev-1",
			"format": "png",
			"size_bytes": 12345,
			"timestamp": "2025-12-09T12:34:56Z"
		}
		```
- `GET /sensor/screenshot`
	- Headers: `X-API-Key`
	- Query: `device_id` (optional)
	- 200 Response: array of latest 100 screenshot metadata (no image bytes).
- `GET /sensor/screenshot/{id}`
	- Headers: `X-API-Key`
	- 200 Response: raw binary data of the screenshot. Content-Type inferred from `format` (e.g., `image/png`).
- `GET /sensor/screenshot/latest`
	- Headers: `X-API-Key`
	- Query: `device_id` (optional to get latest for specific device)
	- 200 Response: raw binary data of the latest screenshot, with inferred Content-Type.

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
	-d '{"device_name":"dev-1"}'

# Create temperature data
# Upload screenshot
curl -X POST http://localhost:5000/sensor/screenshot \
	-H "X-API-Key: <api_key>" \
	-F device_id=dev-1 \
	-F format=png \
	-F image=@/path/to/image.png

# List screenshots
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/sensor/screenshot?device_id=dev-1"

# Download screenshot by id
curl -H "X-API-Key: <api_key>" \
	-o screenshot.bin \
	"http://localhost:5000/sensor/screenshot/1"

# Download latest screenshot
curl -H "X-API-Key: <api_key>" \
	-o latest.png \
	"http://localhost:5000/sensor/screenshot/latest"

# Download latest screenshot for specific device
curl -H "X-API-Key: <api_key>" \
	-o latest.png \
	"http://localhost:5000/sensor/screenshot/latest?device_id=dev-1"
curl -X POST http://localhost:5000/temperature \
	-H "Content-Type: application/json" \
	-H "X-API-Key: <api_key>" \
	-d '{"device_id":"dev-1","temperature_celsius":22.5,"humidity_percent":45.2}'

# List temperature data
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/temperature?device_id=dev-1"

# Get latest temperature data (any device)
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/sensor/temperature/latest"

# Get latest temperature data for specific device
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/sensor/temperature/latest?device_id=dev-1"

# Create log
curl -X POST http://localhost:5000/logs \
	-H "Content-Type: application/json" \
	-H "X-API-Key: <api_key>" \
	-d '{"device_id":"dev-1","message":"boot complete"}'

# List logs
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/logs?device_id=dev-1"

# Get latest log (any device)
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/logs/latest"

# Get latest log for specific device
curl -H "X-API-Key: <api_key>" \
	"http://localhost:5000/logs/latest?device_id=dev-1"
```
