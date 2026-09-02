from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import logging

HOST = "0.0.0.0"
PORT = 5000

API_KEY = os.getenv("API_KEY")

DATA_FILE = "/home/aman/my-server/data.json"
LOG_FILE = "/home/aman/my-server/server.log"


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class MyServer(BaseHTTPRequestHandler):

    def send_json(self, status, message, data=None):
        response_data = {
            "status": status,
            "message": message
        }

        if data is not None:
            response_data["data"] = data

        response = json.dumps(response_data).encode()

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

            self.send_json(
                401,
                "Unauthorized"
            )

            return False

        return True

    def log_message(self, format, *args):
        logger.info(
            "%s - %s",
            self.client_address[0],
            format % args
        )

    def do_GET(self):

        logger.info("GET request: %s", self.path)

        if self.path == "/health":

            self.send_json(
                200,
                "Server is healthy"
            )

        elif self.path == "/api":

            self.send_json(
                200,
                "Python Server is running!"
            )

        elif self.path == "/status":

            self.send_json(
                200,
                "Server is online",
                {
                    "server": "Python",
                    "port": PORT
                }
            )

        elif self.path == "/data":

            if not self.check_api_key():
                return

            try:
                with open(DATA_FILE, "r") as file:
                    data = json.load(file)

                self.send_json(
                    200,
                    "Data retrieved successfully",
                    data
                )

            except Exception as e:

                logger.error("Error reading data: %s", e)

                self.send_json(
                    500,
                    "Error reading data"
                )

        else:

            self.send_json(
                404,
                "Endpoint not found"
            )

    def do_POST(self):

        logger.info("POST request: %s", self.path)

        if self.path != "/data":

            self.send_json(
                404,
                "Endpoint not found"
            )
            return

        if not self.check_api_key():
            return

        try:

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length).decode()

            data = json.loads(body)

            with open(DATA_FILE, "w") as file:
                json.dump(data, file, indent=4)

            logger.info("Data updated successfully")

            self.send_json(
                200,
                "Data updated successfully",
                data
            )

        except json.JSONDecodeError:

            logger.warning("Invalid JSON received")

            self.send_json(
                400,
                "Invalid JSON"
            )

        except Exception as e:

            logger.error("Error saving data: %s", e)

            self.send_json(
                500,
                "Error saving data"
            )


server = HTTPServer(
    (HOST, PORT),
    MyServer
)

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
