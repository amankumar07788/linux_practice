import os
import json
import sqlite3
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# =========================
# CONFIGURATION
# =========================

HOST = "0.0.0.0"
PORT = 5000

BASE_DIR = "/home/aman/my-server"
DB_FILE = os.path.join(BASE_DIR, "server.db")
LOG_FILE = os.path.join(BASE_DIR, "server.log")
ENV_FILE = os.path.join(BASE_DIR, ".env")


# =========================
# LOAD .ENV
# =========================

def load_env_file():
    if not os.path.exists(ENV_FILE):
        return

    try:
        with open(ENV_FILE, "r") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)

                    key = key.strip()
                    value = value.strip()

                    if key and value:
                        os.environ.setdefault(key, value)

    except Exception as e:
        print(f"Could not load .env: {e}")


load_env_file()

API_KEY = os.getenv("API_KEY")


# =========================
# LOGGING
# =========================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================
# DATABASE
# =========================

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            course TEXT,
            version TEXT
        )
        """
    )

    conn.commit()
    conn.close()


# =========================
# DATABASE FUNCTIONS
# =========================

def get_data():
    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT id, name, course, version
        FROM data
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    data = []

    for row in rows:
        data.append(
            {
                "id": row["id"],
                "name": row["name"],
                "course": row["course"],
                "version": row["version"]
            }
        )

    return data


def save_data(data):
    conn = get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO data (name, course, version)
        VALUES (?, ?, ?)
        """,
        (
            data.get("name"),
            data.get("course"),
            data.get("version")
        )
    )

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return new_id


def update_data(record_id, data):
    conn = get_db_connection()

    cursor = conn.execute(
        """
        UPDATE data
        SET name = ?, course = ?, version = ?
        WHERE id = ?
        """,
        (
            data.get("name"),
            data.get("course"),
            data.get("version"),
            record_id
        )
    )

    conn.commit()

    affected_rows = cursor.rowcount

    conn.close()

    return affected_rows


def delete_data(record_id):
    conn = get_db_connection()

    cursor = conn.execute(
        """
        DELETE FROM data
        WHERE id = ?
        """,
        (record_id,)
    )

    conn.commit()

    affected_rows = cursor.rowcount

    conn.close()

    return affected_rows


# =========================
# HTTP SERVER
# =========================

class MyServer(BaseHTTPRequestHandler):

    # -------------------------
    # JSON RESPONSE
    # -------------------------

    def send_json(self, status_code, data):

        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)


    # -------------------------
    # API KEY CHECK
    # -------------------------

    def check_api_key(self):

        client_key = self.headers.get("X-API-Key")

        if not API_KEY:
            logging.error("API_KEY is not configured")

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Server API key is not configured"
                }
            )

            return False

        if client_key != API_KEY:

            logging.warning(
                "Unauthorized request from %s",
                self.client_address[0]
            )

            self.send_json(
                401,
                {
                    "status": "error",
                    "message": "Unauthorized"
                }
            )

            return False

        return True


    # -------------------------
    # GET
    # -------------------------

    def do_GET(self):

        logging.info(
            "GET request received: %s",
            self.path
        )

        # /health
        if self.path == "/health":

            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Server is healthy"
                }
            )

            return


        # /status
        if self.path == "/status":

            self.send_json(
                200,
                {
                    "status": "ok",
                    "server": "my-server",
                    "port": PORT
                }
            )

            return


        # /api
        if self.path == "/api":

            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "My Server API",
                    "endpoints": [
                        "GET /health",
                        "GET /status",
                        "GET /data",
                        "POST /data",
                        "PUT /data",
                        "DELETE /data"
                    ]
                }
            )

            return


        # /data
        if self.path == "/data":

            if not self.check_api_key():
                return

            try:

                data = get_data()

                self.send_json(
                    200,
                    {
                        "status": "ok",
                        "count": len(data),
                        "data": data
                    }
                )

            except Exception as e:

                logging.error(
                    "GET /data error: %s",
                    e
                )

                self.send_json(
                    500,
                    {
                        "status": "error",
                        "message": "Internal server error"
                    }
                )

            return


        # Unknown endpoint

        self.send_json(
            404,
            {
                "status": "error",
                "message": "Endpoint not found"
            }
        )


    # -------------------------
    # POST
    # -------------------------

    def do_POST(self):

        logging.info(
            "POST request received: %s",
            self.path
        )

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
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            new_data = json.loads(
                body.decode("utf-8")
            )


            if not isinstance(new_data, dict):

                self.send_json(
                    400,
                    {
                        "status": "error",
                        "message": "JSON must be an object"
                    }
                )

                return


            new_id = save_data(new_data)


            self.send_json(
                201,
                {
                    "status": "ok",
                    "message": "Data created successfully",
                    "data": {
                        "id": new_id,
                        "name": new_data.get("name"),
                        "course": new_data.get("course"),
                        "version": new_data.get("version")
                    }
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

            logging.error(
                "POST error: %s",
                e
            )

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Internal server error"
                }
            )


    # -------------------------
    # PUT
    # -------------------------

    def do_PUT(self):

        logging.info(
            "PUT request received: %s",
            self.path
        )

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
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            new_data = json.loads(
                body.decode("utf-8")
            )


            if not isinstance(new_data, dict):

                self.send_json(
                    400,
                    {
                        "status": "error",
                        "message": "JSON must be an object"
                    }
                )

                return


            record_id = new_data.get("id")


            if not record_id:

                self.send_json(
                    400,
                    {
                        "status": "error",
                        "message": "ID is required for PUT"
                    }
                )

                return


            affected_rows = update_data(
                record_id,
                new_data
            )


            if affected_rows == 0:

                self.send_json(
                    404,
                    {
                        "status": "error",
                        "message": "Data not found"
                    }
                )

                return


            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Data updated successfully",
                    "data": {
                        "id": record_id,
                        "name": new_data.get("name"),
                        "course": new_data.get("course"),
                        "version": new_data.get("version")
                    }
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

            logging.error(
                "PUT error: %s",
                e
            )

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Internal server error"
                }
            )


    # -------------------------
    # DELETE
    # -------------------------

    def do_DELETE(self):

        logging.info(
            "DELETE request received: %s",
            self.path
        )

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
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            )

            delete_data_request = json.loads(
                body.decode("utf-8")
            )


            if not isinstance(
                delete_data_request,
                dict
            ):

                self.send_json(
                    400,
                    {
                        "status": "error",
                        "message": "JSON must be an object"
                    }
                )

                return


            record_id = delete_data_request.get(
                "id"
            )


            if not record_id:

                self.send_json(
                    400,
                    {
                        "status": "error",
                        "message": "ID is required for DELETE"
                    }
                )

                return


            affected_rows = delete_data(
                record_id
            )


            if affected_rows == 0:

                self.send_json(
                    404,
                    {
                        "status": "error",
                        "message": "Data not found"
                    }
                )

                return


            self.send_json(
                200,
                {
                    "status": "ok",
                    "message": "Data deleted successfully",
                    "id": record_id
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

            logging.error(
                "DELETE error: %s",
                e
            )

            self.send_json(
                500,
                {
                    "status": "error",
                    "message": "Internal server error"
                }
            )


    # -------------------------
    # LOG REQUEST
    # -------------------------

    def log_message(self, format, *args):

        logging.info(
            "%s - %s",
            self.address_string(),
            format % args
        )


# =========================
# START SERVER
# =========================

def run_server():

    initialize_database()

    logging.info(
        "Starting server on %s:%s",
        HOST,
        PORT
    )

    server = ThreadingHTTPServer(
        (HOST, PORT),
        MyServer
    )

    print(
        f"Server running on {HOST}:{PORT}"
    )

    print(
        "Waiting for requests..."
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nServer stopped."
        )

    finally:

        server.server_close()

        logging.info(
            "Server stopped"
        )


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    run_server()
