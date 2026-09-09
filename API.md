# My Python Server API

Base URL:

http://127.0.0.1:5000

## 1. Health Check

GET /health

No API key required.

## 2. API Status

GET /api

No API key required.

## 3. Server Status

GET /status

No API key required.

## 4. Get Data

GET /data

Header:

X-API-Key: YOUR_API_KEY

## 5. Create Data

POST /data

Headers:

Content-Type: application/json
X-API-Key: YOUR_API_KEY

Example:

{
    "name": "Aman",
    "course": "Python Server"
}

## 6. Replace Data

PUT /data

Headers:

Content-Type: application/json
X-API-Key: YOUR_API_KEY

## 7. Delete Data

DELETE /data

Header:

X-API-Key: YOUR_API_KEY

## Authentication

Protected endpoints require:

X-API-Key

Requests without a valid API key return:

401 Unauthorized
