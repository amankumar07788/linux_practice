import requests

SERVER = "http://127.0.0.1:5000"
API_KEY = "AMAN123"
TIMEOUT = 5

HEADERS = {
    "X-API-Key": API_KEY
}


def make_request(method, url, **kwargs):
    try:
        response = requests.request(
            method,
            url,
            timeout=TIMEOUT,
            **kwargs
        )

        print("\nHTTP Status:", response.status_code)
        print("Response:")

        try:
            print(response.json())
        except ValueError:
            print(response.text)

    except requests.exceptions.Timeout:
        print("\nError: Server request timed out.")

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server.")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest error: {e}")


def health_check():
    make_request("GET", f"{SERVER}/health")


def get_data():
    make_request(
        "GET",
        f"{SERVER}/data",
        headers=HEADERS
    )


def update_data():
    data = {
        "name": "Aman",
        "course": "Python Server",
        "step": "28"
    }

    make_request(
        "POST",
        f"{SERVER}/data",
        headers=HEADERS,
        json=data
    )


def server_status():
    make_request("GET", f"{SERVER}/status")


def main():
    while True:
        print("\n==============================")
        print("      PYTHON SERVER CLIENT")
        print("==============================")
        print("1. Health Check")
        print("2. Get Data")
        print("3. Update Data")
        print("4. Server Status")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            health_check()

        elif choice == "2":
            get_data()

        elif choice == "3":
            update_data()

        elif choice == "4":
            server_status()

        elif choice == "5":
            print("Client exited.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
