import requests
import sqlite3
import os

def test_login():
    # 1. Get a user from DB
    if not os.path.exists("quiz_data.db"):
        print("DB not found in CWD")
        return

    conn = sqlite3.connect("quiz_data.db")
    c = conn.cursor()
    c.execute("SELECT email FROM users LIMIT 1")
    user = c.fetchone()
    conn.close()

    if not user:
        print("No users in DB to test with.")
        return

    email = user[0]
    print(f"Testing login for: {email}")
    
    # We don't know the password, but we can check if the API is reachable
    # and returns 401 (Auth failed) vs 500 (Server error) vs ConnectionRefused
    
    url = "http://127.0.0.1:8000/auth/login"
    payload = {
        "email": email,
        "password": "wrongpasswordtest" 
    }
    
    try:
        print(f"POST {url} ...")
        res = requests.post(url, json=payload)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        
        if res.status_code == 401:
            print("SUCCESS: API reachable, Auth logic working (rejected wrong password)")
        elif res.status_code == 200:
            print("SUCCESS: Logged in?!")
        else:
            print("FAILURE: Unexpected status code")
            
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    test_login()
