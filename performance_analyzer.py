import sqlite3
from config import DATABASE_PATH


def get_chapter_performance(chapter_name: str) -> dict:
    """Return topic-level stats for a chapter."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT topic, score, total FROM progress WHERE chapter = ?",
        (chapter_name,)
    )
    rows = cursor.fetchall()
    conn.close()

    result = {}
    for topic, score, total in rows:
        pct = round((score / total * 100) if total > 0 else 0, 1)
        result[topic] = {"score": score, "total": total, "percentage": pct}
    return result


def get_all_performance() -> list:
    """Return all progress records."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT chapter, topic, score, total, timestamp FROM progress ORDER BY timestamp DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "chapter": r[0], "topic": r[1], "score": r[2],
            "total": r[3],
            "percentage": round((r[2] / r[3] * 100) if r[3] > 0 else 0, 1),
            "timestamp": r[4]
        }
        for r in rows
    ]