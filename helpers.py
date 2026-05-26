import re
import os


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def score_color(pct: float) -> str:
    if pct >= 80:
        return 'success'
    elif pct >= 60:
        return 'warning'
    return 'danger'


def score_emoji(pct: float) -> str:
    if pct >= 80:
        return '🎉'
    elif pct >= 60:
        return '👍'
    return '💪'