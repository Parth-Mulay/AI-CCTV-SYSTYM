import os
import sqlite3
from werkzeug.security import generate_password_hash
import sqlite3

DB_PATH = "database.db"  # relative path to your main project folder


# Use your actual DB path here:
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.db')

def register_user(user_id, username, email, role, hashed_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, email, role, password)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, email, role, hashed_password))
    conn.commit()
    conn.close()

def get_user_by_username_or_id(username_or_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, email, role, password
        FROM users
        WHERE username = ? OR user_id = ?
    """, (username_or_id, username_or_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "email": row[2],
            "role": row[3],
            "password": row[4],
        }
    return None

def get_user(user_id):
    # Helper to get user by user_id only
    return get_user_by_username_or_id(user_id)
