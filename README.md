# Python Server Software

A simple Python HTTP server with:

- REST API endpoints
- API key authentication
- JSON data storage
- Client application
- Server logging
- Log rotation
- Systemd service
- Git and GitHub integration

## API Endpoints

### Health Check

GET `/health`

### Server API

GET `/api`

### Server Status

GET `/status`

### Protected Data

GET `/data`

Requires:

`X-API-Key`

### Update Data

POST `/data`

Requires:

`X-API-Key`

## Run Client

```bash
python3 client.py
