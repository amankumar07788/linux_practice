# Python Server Software

A lightweight HTTP server built with Python, SQLite and API-key authentication.

## Features

- HTTP server using Python
- REST-style CRUD API
- SQLite database
- API-key authentication
- JSON request and response
- Multiple records
- Logging
- systemd service
- Health and status endpoints
- Error handling

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Server health |
| GET | `/status` | Server status |
| GET | `/api` | API information |
| GET | `/data` | Get all records |
| POST | `/data` | Create a record |
| PUT | `/data` | Update a record by ID |
| DELETE | `/data` | Delete a record by ID |

## Authentication

Protected `/data` endpoints require:

`X-API-Key`

Example:

```bash
curl -H "X-API-Key: AMAN123" http://127.0.0.1:5000/data
