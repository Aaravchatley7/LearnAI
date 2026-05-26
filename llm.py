"""
llm.py — Two-tier LLM routing:
  • Groq  (llama-3.3-70b-versatile) — fast, used for MCQs + summaries + topics
  • OpenRouter (mistral-7b-instruct) — fallback when Groq key missing/fails
"""
import json
import re
import requests
from config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL,
    GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL,
)


# ── JSON helper ────────────────────────────────────────────────────────────────
def _clean_json(raw: str):
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        for pat in [r'(\[[\s\S]*?\])', r'(\{[\s\S]*?\})']:
            m = re.search(pat, cleaned, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception:
                    pass
    return None


# ── Groq — primary (fast: ~1-2s) ──────────────────────────────────────────────
def ask_groq(prompt: str, system: str = None, temperature: float = 0.7, max_tokens: int = 1500) -> str:
    if not GROQ_API_KEY:
        return ask_llm(prompt, system=system, temperature=temperature, max_tokens=max_tokens)
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": GROQ_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    try:
        r = requests.post(GROQ_BASE_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[Groq ERROR] {e} — falling back to OpenRouter")
        return ask_llm(prompt, system=system, temperature=temperature, max_tokens=max_tokens)


def ask_groq_json(prompt: str, system: str = None, temperature: float = 0.3):
    sys_msg = ((system or "") + "\nReturn ONLY valid JSON. No markdown, no explanation.").strip()
    raw = ask_groq(prompt, system=sys_msg, temperature=temperature, max_tokens=2000)
    return _clean_json(raw)


# ── OpenRouter — fallback ──────────────────────────────────────────────────────
def ask_llm(prompt: str, system: str = None, temperature: float = 0.7, max_tokens: int = 1500) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI eLearning System",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": DEFAULT_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    try:
        r = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[OpenRouter ERROR] {e}")
        return ""


def ask_llm_json(prompt: str, system: str = None, temperature: float = 0.3):
    sys_msg = ((system or "") + "\nReturn ONLY valid JSON. No markdown, no explanation.").strip()
    raw = ask_llm(prompt, system=sys_msg, temperature=temperature, max_tokens=2000)
    return _clean_json(raw)
