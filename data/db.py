import sqlite3

DB_NAME = "checkpoint.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        platform TEXT,
        genre_mode TEXT,
        notes TEXT,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()