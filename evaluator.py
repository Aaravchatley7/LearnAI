from models.llm import ask_llm


def get_weak_topics(topic_scores: dict) -> list:
    """Return topics where score percentage is below 60%."""
    return [topic for topic, pct in topic_scores.items() if pct < 60]


def generate_reexplanation(topic_name: str, wrong_questions: list = None) -> str:
    """Re-explain a weak topic in simpler terms."""
    q_block = ""
    if wrong_questions:
        q_block = "\nThe student got these questions wrong:\n" + "\n".join(f"- {q}" for q in wrong_questions)

    prompt = f"""A student is struggling with: "{topic_name}"{q_block}

Re-explain "{topic_name}" in the simplest possible way:
- Use language a 12-year-old would understand
- Give 2–3 concrete real-life examples or analogies
- Keep it positive and encouraging
- 3 short paragraphs maximum

Write the re-explanation:"""

    return ask_llm(prompt, temperature=0.6, max_tokens=600)