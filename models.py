import sqlite3
from passlib.hash import bcrypt

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )""")
    conn.commit()
    conn.close()

def add_user(username, password, role="user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  (username, bcrypt.hash(password), role))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def find_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username,password,role FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return {"username": row[0], "password": row[1], "role": row[2]} if row else None
