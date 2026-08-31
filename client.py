import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000"
API_KEY = "AMAN123"


def get_request(endpoint, protected=False):
    try:
        headers = {}

        if protected:
            headers["X-API-Key"] = API_KEY

        request = urllib.request.Request(
            BASE_URL + endpoint,
            headers=headers
        )

        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())

    except Exception as e:
        return {"error": str(e)}


def post_data(data):
    try:
        json_data = json.dumps(data).encode()

        request = urllib.request.Request(
            BASE_URL + "/data",
            data=json_data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            },
            method="POST"
        )

        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())

    except Exception as e:
        return {"error": str(e)}


while True:

    print("\n===== PYTHON SERVER CLIENT =====")
    print("1. Health Check")
    print("2. Get Data")
    print("3. Update Data")
    print("4. Server Status")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        result = get_request("/health")
        print(json.dumps(result, indent=4))

    elif choice == "2":
        result = get_request("/data", protected=True)
        print(json.dumps(result, indent=4))

    elif choice == "3":
        name = input("Enter name: ")
        course = input("Enter course: ")

        data = {
            "name": name,
            "course": course
        }

        result = post_data(data)
        print(json.dumps(result, indent=4))

    elif choice == "4":
        result = get_request("/status")
        print(json.dumps(result, indent=4))

    elif choice == "5":
        print("Client closed.")
        break

    else:
        print("Invalid choice!")
