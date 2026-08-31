from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

HOST = "0.0.0.0"
PORT = 5000

API_KEY = "AMAN123"

DATA_FILE = "/home/aman/my-server/data.json"
LOG_FILE = "/home/aman/my-server/server.log"


# Logging setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class MyServer(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        response = json.dumps(data).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)

    def check_api_key(self):
        key = self.headers.get("X-API-Key")

        if key != API_KEY:
            logger.warning(
                "Unauthorized request from %s",
                self.client_address[0]
            )

            self.send_json({
                "status": "error",
                "message": "Unauthorized"
            }, 401)

            return False

        return True

    def log_message(self, format, *args):
        logger.info(
            "%s - %s",
            self.client_address[0],
            format % args
        )

    def do_GET(self):

        logger.info("GET request received: %s", self.path)

        if self.path == "/health":

            self.send_json({
                "status": "ok",
                "message": "Server is healthy"
            })

        elif self.path == "/api":

            self.send_json({
                "status": "success",
                "message": "Python Server is running!"
            })

        elif self.path == "/status":

            self.send_json({
                "status": "online",
                "server": "Python",
                "port": PORT
            })

        elif self.path == "/data":

            if not self.check_api_key():
                return

            try:
                with open(DATA_FILE, "r") as file:
                    data = json.load(file)

                self.send_json(data)

            except Exception as e:

                logger.error("Error reading data.json: %s", e)

                self.send_json({
                    "status": "error",
                    "message": str(e)
                }, 500)

        else:

            self.send_json({
                "status": "error",
                "message": "Endpoint not found"
            }, 404)

    def do_POST(self):

        logger.info("POST request received: %s", self.path)

        if self.path == "/data":

            if not self.check_api_key():
                return

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length).decode()

            try:
                data = json.loads(body)

                with open(DATA_FILE, "w") as file:
                    json.dump(data, file, indent=4)

                logger.info("Data updated successfully")

                self.send_json({
                    "status": "success",
                    "message": "Data updated successfully",
                    "data": data
                })

            except json.JSONDecodeError:

                logger.warning("Invalid JSON received")

                self.send_json({
                    "status": "error",
                    "message": "Invalid JSON"
                }, 400)

            except Exception as e:

                logger.error("Error saving data: %s", e)

                self.send_json({
                    "status": "error",
                    "message": str(e)
                }, 500)

        else:

            self.send_json({
                "status": "error",
                "message": "Endpoint not found"
            }, 404)


server = HTTPServer((HOST, PORT), MyServer)

logger.info("Server started on port %s", PORT)

print(f"Server running on port {PORT}...")
print("Waiting for HTTP requests...")

try:
    server.serve_forever()

except KeyboardInterrupt:
    print("\nServer stopped.")
    logger.info("Server stopped manually")

finally:
    server.server_close()
    logger.info("Server closed")
