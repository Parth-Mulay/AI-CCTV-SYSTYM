import sqlite3
import os

DB_PATH = "database.db"  # Make sure this matches your user.py DB_PATH

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT,
                role TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized: users table created.")
    else:
        print("Database already exists. Skipping initialization.")

if __name__ == "__main__":
    init_db()