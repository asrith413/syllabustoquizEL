import requests
import sys

try:
    print("Testing Backend Connection...")
    # 1. Test if server is reachable
    try:
        requests.get("http://127.0.0.1:8000/docs", timeout=2)
        print("Backend is reachable.")
    except requests.exceptions.ConnectionError:
        print("Backend is NOT reachable. Is it running?")
        sys.exit(1)

    # 2. Test Signup
    print("Testing Signup...")
    payload = {
        "email": "test_debug@example.com",
        "username": "debug_user",
        "password": "password123"
    }
    response = requests.post("http://127.0.0.1:8000/auth/signup", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")
