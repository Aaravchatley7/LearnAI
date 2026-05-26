from models.llm import ask_groq  # Groq = fast


def generate_summary(chapter_text: str) -> str:
    """Generate a student-friendly chapter summary via Groq (~1-2s)."""
    # Trim to 5000 chars — enough context, keeps tokens low → faster
    truncated = chapter_text[:5000]

    system = "You are a concise educational writer. Summarise clearly for students."

    prompt = f"""Summarise this chapter for a student in 3 short paragraphs.
- Simple language, no bullet points, no "This chapter..." opener
- Highlight only the core ideas

CHAPTER:
{truncated}

Summary:"""

    return ask_groq(prompt, system=system, temperature=0.4, max_tokens=500)
