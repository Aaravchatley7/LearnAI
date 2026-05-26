"""
MCQ Generator — uses Groq (fast) with OpenRouter as fallback.

Why Groq:
  - llama-3.3-70b-versatile returns in ~1–2 s vs 8–15 s on OpenRouter
  - Free tier: 6000 req/day, 500K tokens/day
  - Falls back automatically to OpenRouter if key is missing or call fails
"""
import re
import random
from models.llm import ask_groq_json, ask_groq


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_mcqs(topic_name: str, chapter_context: str = "", count: int = 4) -> list:
    """
    Generate `count` topic-specific MCQs via Groq.
    Returns list of dicts:
      { "question": str, "options": {"A":str, "B":str, "C":str, "D":str}, "correct": "A"|"B"|"C"|"D" }
    """
    context_block = (
        f"\nBase your questions on this chapter content:\n{chapter_context[:3000]}\n"
        if chapter_context else ""
    )

    # Random focus so questions vary each call
    focus_hints = [
        "Focus on definitions and core concepts.",
        "Focus on real-world applications and examples.",
        "Focus on comparisons and relationships between ideas.",
        "Focus on causes, effects, and consequences.",
        "Focus on processes, sequences, or how things work.",
        "Focus on advantages, disadvantages, or limitations.",
    ]
    hint = random.choice(focus_hints)

    system = (
        "You are an expert quiz creator for an eLearning platform. "
        "You always return valid JSON with no extra text."
    )

    prompt = f"""Generate exactly {count} multiple-choice questions about: "{topic_name}"
{context_block}
Rules:
- Every question MUST be clearly about "{topic_name}" — not generic trivia.
- {hint}
- Each question has options A, B, C, D. Exactly ONE is correct.
- Distractors must be plausible but wrong.
- Vary difficulty across questions (easy / medium / hard).
- Vary which letter (A/B/C/D) is the correct answer — do NOT make every answer "A".
- "correct" must be exactly one of: "A", "B", "C", "D"

Return ONLY a JSON array:
[
  {{
    "question": "...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct": "B"
  }}
]"""

    result = ask_groq_json(prompt, system=system, temperature=0.85)

    if isinstance(result, list) and result:
        validated = [v for v in (_validate(item) for item in result) if v]
        if validated:
            return validated[:count]

    # Plain-text fallback (also via Groq/OpenRouter)
    return _text_fallback(topic_name, count)


# ── Validation ─────────────────────────────────────────────────────────────────

def _validate(item) -> dict | None:
    if not isinstance(item, dict):
        return None

    question = str(item.get("question", "")).strip()
    options  = item.get("options", {})
    correct  = str(item.get("correct", "")).strip().upper()

    if not question:
        return None

    # Accept a list of 4 options
    if isinstance(options, list) and len(options) == 4:
        labels = ["A", "B", "C", "D"]
        options = {
            labels[i]: re.sub(r'^[A-Da-d][.)]\s*', '', str(o)).strip()
            for i, o in enumerate(options)
        }

    if not isinstance(options, dict):
        return None

    # Normalise keys — ensure A/B/C/D all present
    normalized = {}
    for label in ["A", "B", "C", "D"]:
        val = options.get(label) or options.get(label.lower())
        if not val:
            return None
        normalized[label] = str(val).strip()

    # Validate correct key
    if correct not in ("A", "B", "C", "D"):
        correct = _infer_correct(item.get("correct", ""), normalized) or "A"

    return {"question": question, "options": normalized, "correct": correct}


def _infer_correct(raw: str, options: dict) -> str | None:
    raw = str(raw).strip()
    m = re.match(r'^([A-Da-d])[.)]\s*', raw)
    if m:
        return m.group(1).upper()
    for key, val in options.items():
        if raw.lower() == val.lower() or raw.lower() in val.lower():
            return key
    return None


# ── Fallbacks ──────────────────────────────────────────────────────────────────

def _text_fallback(topic_name: str, count: int) -> list:
    """Ask for MCQs in a plain-text format and parse the result."""
    prompt = f"""Create {count} quiz questions about "{topic_name}".
Use this EXACT format for each (do not deviate):

Q: [question text]
A: [option A]
B: [option B]
C: [option C]
D: [option D]
CORRECT: [single letter: A, B, C, or D]

---

Vary the CORRECT letter across questions. Make every question specific to "{topic_name}"."""

    raw = ask_groq(prompt, temperature=0.8, max_tokens=1200)
    parsed = _parse_text_mcqs(raw)
    return parsed[:count] if parsed else _emergency_mcqs(topic_name, count)


def _parse_text_mcqs(text: str) -> list:
    mcqs   = []
    blocks = re.split(r'\n---+\n|\n\n(?=Q:)', text.strip())

    for block in blocks:
        q       = re.search(r'Q:\s*(.+?)(?=\n[ABCD]:)', block, re.DOTALL)
        opts    = re.findall(r'([ABCD]):\s*(.+?)(?=\n[ABCD]:|\nCORRECT:|$)', block, re.DOTALL)
        correct = re.search(r'CORRECT:\s*([ABCD])', block, re.IGNORECASE)

        if q and len(opts) == 4 and correct:
            mcqs.append({
                "question": q.group(1).strip(),
                "options":  {lbl: txt.strip() for lbl, txt in opts},
                "correct":  correct.group(1).upper(),
            })

    return mcqs


def _emergency_mcqs(topic_name: str, count: int) -> list:
    """Last resort: generic but structurally valid MCQs."""
    pool = [
        {
            "question": f"Which statement best describes '{topic_name}'?",
            "options": {
                "A": "A fundamental concept in this field of study",
                "B": "An unrelated historical event",
                "C": "A cooking technique",
                "D": "A type of sports equipment",
            },
            "correct": "A",
        },
        {
            "question": f"Why is '{topic_name}' important to study?",
            "options": {
                "A": "It has no practical value",
                "B": "It builds a foundation for further learning in this subject",
                "C": "It only applies to ancient civilisations",
                "D": "It is relevant only to PhD researchers",
            },
            "correct": "B",
        },
        {
            "question": f"'{topic_name}' is primarily associated with:",
            "options": {
                "A": "Music composition",
                "B": "This academic subject and related disciplines",
                "C": "Culinary arts",
                "D": "Athletic training",
            },
            "correct": "B",
        },
        {
            "question": f"A student who understands '{topic_name}' will be able to:",
            "options": {
                "A": "Apply its core principles to solve related problems",
                "B": "Recite unrelated mathematical tables",
                "C": "Identify ancient artefacts",
                "D": "Navigate using a compass",
            },
            "correct": "A",
        },
    ]
    return pool[:count]
