import sqlite3

DATABASE_PATH = "database/elearning.db"


def save_progress(chapter, topic, score, total):

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO progress
        (chapter, topic, score, total)
        VALUES (?, ?, ?, ?)
    """, (chapter, topic, score, total))

    conn.commit()
    conn.close()


def get_all_progress():

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT chapter, topic, score, total, timestamp
        FROM progress
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows