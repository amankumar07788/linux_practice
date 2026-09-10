import os
import json
import sqlite3
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dotenv import load_dotenv

load_dotenv("/home/aman/my-server/.env")

HOST = "0.0.0.0"
PORT = 5000

API_KEY = os.getenv("API_KEY")

DB_FILE = "/home/aman/my-server/server.db"
LOG_FILE = "/home/aman/my-server/server.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def save_data(data):
    conn = get_db_connection()

    conn.execute("DELETE FROM data")

    conn.execute(
        "INSERT INTO data (name, course, version) VALUES (?, ?, ?)",
        (
            data.get("name"),
            data.get("course"),
            data.get("version")
        )
    )

    conn.commit()
    conn.close()


def get_data():
    conn = get_db_connection()

    row = conn.execute(
        "SELECT name, course, version FROM data ORDER BY id DESC LIMIT 1"
    ).fetchone()

    conn.close()

    if row is None:
        return {}

    return {
        "name": row["name"],
        "course": row["course"],
        "version": row["version"]
    }


def delete_data():
    conn = get_db_connection()
    conn.execute("DELETE FROM data")
    conn.commit()
    conn.close()


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

            data = get_data()

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

            save_data(new_data)

            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Data created successfully",
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

            save_data(new_data)

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
            delete_data()

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
    server = ThreadingHTTPServer(
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
