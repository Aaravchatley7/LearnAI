import os

UPLOAD_FOLDER    = "uploads"
DATABASE_PATH    = "database/elearning.db"

# ── OpenRouter (summaries, explanations, topic extraction) ────────────────────
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL       = "mistralai/mistral-7b-instruct"   # fixed model string

# ── Groq (fast MCQ generation) ────────────────────────────────────────────────
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "").strip()
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL    = "llama-3.3-70b-versatile"   # fastest, highest quality on Groq
