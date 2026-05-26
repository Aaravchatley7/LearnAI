import re
from models.llm import ask_groq_json  # Groq for fast LLM fallback


def detect_chapters(text: str) -> dict:
    chapters = _regex_detect(text)
    if len(chapters) >= 2:
        return chapters
    return _llm_detect(text)


def _regex_detect(text: str) -> dict:
    patterns = [
        r'(?m)^(Chapter\s+[\dIVXLCivxlc]+[\s\.:—–-]*[^\n]*)',
        r'(?m)^(CHAPTER\s+[\dIVXLCivxlc]+[\s\.:—–-]*[^\n]*)',
        r'(?m)^(UNIT\s+\d+[\s\.:—–-]*[^\n]*)',
        r'(?m)^(Section\s+\d+[\s\.:—–-]*[^\n]*)',
        r'(?m)^(\d+\.\s+[A-Z][^\n]{5,50}$)',
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        if len(matches) >= 2:
            return _build_from_matches(text, matches)
    return {}


def _build_from_matches(text: str, matches: list) -> dict:
    chapters = {}
    for i, match in enumerate(matches):
        title = " ".join(match.group(1).replace("\n", " ").split()).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        key = title if title not in chapters else f"{title} ({i+1})"
        chapters[key] = text[start:end].strip()
    return chapters


def _llm_detect(text: str) -> dict:
    prompt = f"""List all chapter/section titles from this text.

TEXT:
{text[:4000]}

Return ONLY a JSON array of titles, e.g.:
["Introduction", "Chapter 1: Basics", "Chapter 2: Advanced"]"""

    result = ask_groq_json(prompt)
    if not isinstance(result, list) or not result:
        return _chunk_fallback(text)

    titles = [" ".join(str(t).replace("\n", " ").split()).strip() for t in result if t]
    chapters = {}
    for i, title in enumerate(titles):
        idx = text.find(title)
        if idx == -1:
            idx = text.lower().find(title.lower())
        if idx == -1:
            continue
        next_idx = len(text)
        if i + 1 < len(titles):
            ni = text.find(titles[i + 1], idx + 1)
            if ni == -1:
                ni = text.lower().find(titles[i + 1].lower(), idx + 1)
            if ni != -1:
                next_idx = ni
        chapters[title] = text[idx:next_idx].strip()
    return chapters if chapters else _chunk_fallback(text)


def _chunk_fallback(text: str) -> dict:
    words = text.split()
    wpc = 500
    n = max(1, len(words) // wpc)
    return {f"Section {i+1}": " ".join(words[i*wpc:(i+1)*wpc]) for i in range(n)}
