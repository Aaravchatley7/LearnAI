import sqlite3
import os

DATABASE_PATH = "database/elearning.db"


def init_db():

    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter TEXT,
            topic TEXT,
            score INTEGER,
            total INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()