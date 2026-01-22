import sqlite3
import os

db_path = "quiz_data.db"
if not os.path.exists(db_path):
    print(f"Database file {db_path} NOT FOUND!")
else:
    print(f"Database file found at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n--- Tables Found ---")
    for t in tables:
        print(f"- {t[0]}")
    
    # helper to print count
    def print_count(table_name):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n[{table_name}] Total records: {count}")
            return count
        except:
            print(f"\n[{table_name}] (Table not found or error)")
            return 0

    print("\n--- Data Statistics ---")
    print_count("users")
    print_count("sessions")
    print_count("quizzes")
    print_count("submissions")

    # Show recent users
    print("\n--- Recent Users ---")
    try:
        cursor.execute("SELECT email, username, created_at FROM users ORDER BY created_at DESC LIMIT 5")
        users = cursor.fetchall()
        for u in users:
            print(f"User: {u[1]} ({u[0]}) - Created: {u[2]}")
    except:
        pass

    conn.close()
