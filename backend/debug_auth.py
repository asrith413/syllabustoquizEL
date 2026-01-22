from database.database import Database
import os
import sys

# Ensure we can import from database
sys.path.append(os.getcwd())

def test_auth():
    print(f"CWD: {os.getcwd()}")
    db_path = "quiz_data.db"
    print(f"Checking DB: {db_path} (Exists: {os.path.exists(db_path)})")
    
    if not os.path.exists(db_path):
        print("ERROR: Database file not found in current directory!")
        return

    db = Database(db_path)
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id, username, email, created_at FROM users")
        users = cursor.fetchall()
        print(f"\nFound {len(users)} users:")
        for u in users:
            print(f" - {u[1]} ({u[2]}) [ID: {u[0]}]")
            
        if not users:
            print("WARNING: No users found! You may need to Sign Up again.")
            
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    test_auth()
