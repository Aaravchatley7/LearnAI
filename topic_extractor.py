from models.llm import ask_groq_json, ask_groq  # Groq = fast


def extract_topics(summary: str) -> list:
    """Extract 4-6 key topics from a chapter summary via Groq."""
    prompt = f"""Read this chapter summary. List the 4 to 6 most important topics a student must learn.

SUMMARY:
{summary}

Return ONLY a JSON array of short topic names, e.g.:
["Newton's Laws", "Gravitational Force", "Types of Energy"]"""

    result = ask_groq_json(prompt, temperature=0.3)

    if isinstance(result, list) and result:
        return [str(t).strip() for t in result if str(t).strip()]

    # plain-text fallback
    raw = ask_groq(f"List the 5 most important topics from this, one per line:\n\n{summary}",
                   temperature=0.3, max_tokens=200)
    topics = []
    for line in raw.split("\n"):
        line = line.strip().lstrip("0123456789.-) •*")
        if line and len(line) > 3:
            topics.append(line)
    return topics[:6] if topics else ["Core Concepts", "Key Ideas", "Main Principles"]
