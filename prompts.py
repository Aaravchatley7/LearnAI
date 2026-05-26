TOPIC_EXPLANATION_SYSTEM = (
    "You are a brilliant, enthusiastic teacher who explains things clearly "
    "using simple language, real-world analogies, and relatable examples."
)

TOPIC_EXPLANATION_PROMPT = """Explain the topic '{topic}' for a student who is just learning it.

Guidelines:
- Start with the core idea in 1–2 sentences
- Use 2–3 concrete real-world examples or analogies
- Keep language simple and conversational
- 3–4 short paragraphs
- End with a single "Key takeaway:" sentence

Write the explanation now:"""

FINAL_TEST_PROMPT = """Create a 20-question multiple-choice chapter test for: "{chapter}"

Topics covered: {topics}

Rules:
- Spread questions across ALL topics evenly
- Mix easy, medium, and hard questions
- 4 options each (A, B, C, D), exactly one correct
- Vary which letter is correct across questions
- Return ONLY a JSON array:
  [{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct": "B"}}, ...]"""