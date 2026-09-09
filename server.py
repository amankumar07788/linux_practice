import os
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dotenv import load_dotenv

load_dotenv("/home/aman/my-server/.env")

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


def read_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


class MyServer(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)


    def check_api_key(self):
        client_key = self.headers.get("X-API-Key")

        if not client_key or client_key != API_KEY:
            self.send_json(
                401,
                {
                    "status": "error",
                    "message": "Unauthorized"
                }
            )
            return False

        return True


    def do_GET(self):
        logging.info(f"GET request received: {self.path}")

        if self.path == "/health":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Server is healthy"
                }
            )

        elif self.path == "/api":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "API is working"
                }
            )

        elif self.path == "/status":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "server": "Python HTTP Server",
                    "port": PORT
                }
            )

        elif self.path == "/data":

            if not self.check_api_key():
                return

            data = read_data()

            self.send_json(
                200,
                {
                    "status": "ok",
                    "data": data
                }
            )

        else:
            self.send_json(
                404,
                {
                    "status": "error",
                    "message": "Endpoint not found"
                }
            )


    def do_POST(self):
        logging.info(f"POST request received: {self.path}")

        if self.path != "/data":
            self.send_json(
                404,
                {
                    "status": "error",
                    "message": "Endpoint not found"
                }
            )
            return

        if not self.check_api_key():
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            new_data = json.loads(
                body.decode("utf-8")
            )

            write_data(new_data)

            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Data updated successfully",
                    "data": new_data
                }
            )

        except json.JSONDecodeError:
            self.send_json(
                400,
                {
                    "status": "error",
                    "message": "Invalid JSON"
                }
            )

        except Exception as e:
            logging.error(f"POST error: {e}")

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Internal server error"
                }
            )


    def do_PUT(self):
        logging.info(f"PUT request received: {self.path}")

        if self.path != "/data":
            self.send_json(
                404,
                {
                    "status": "error",
                    "message": "Endpoint not found"
                }
            )
            return

        if not self.check_api_key():
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            new_data = json.loads(
                body.decode("utf-8")
            )

            write_data(new_data)

            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Data replaced successfully",
                    "data": new_data
                }
            )

        except json.JSONDecodeError:
            self.send_json(
                400,
                {
                    "status": "error",
                    "message": "Invalid JSON"
                }
            )

        except Exception as e:
            logging.error(f"PUT error: {e}")

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Internal server error"
                }
            )


    def do_DELETE(self):
        logging.info(f"DELETE request received: {self.path}")

        if self.path != "/data":
            self.send_json(
                404,
                {
                    "status": "error",
                    "message": "Endpoint not found"
                }
            )
            return

        if not self.check_api_key():
            return

        try:
            write_data({})

            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Data deleted successfully"
                }
            )

        except Exception as e:
            logging.error(f"DELETE error: {e}")

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Internal server error"
                }
            )


def run_server():
    server =  ThreadingHTTPServer(
        (HOST, PORT),
        MyServer
    )

    logging.info(
        f"Server started on {HOST}:{PORT}"
    )

    print(
        f"Server running on port {PORT}..."
    )

    print("Waiting for requests...")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
