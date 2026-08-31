kimport socket
import json

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(f"Server running on port {PORT}...")
print("Waiting for client...")

while True:
    client, address = server.accept()
    print("Client connected:", address)

    data = client.recv(4096).decode()

    if data:
        print("Data received:", data)

        try:
            received_data = json.loads(data)

            with open("data.json", "w") as file:
                json.dump(received_data, file, indent=4)

            response = {
                "status": "success",
                "message": "JSON received and saved successfully",
                "received_data": received_data
            }

        except json.JSONDecodeError:
            response = {
                "status": "error",
                "message": "Invalid JSON"
            }

        client.send(json.dumps(response).encode())

    client.close()
