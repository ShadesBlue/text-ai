import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(prompt):
    if not GROQ_API_KEY:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a statistical assistant. Return ONLY valid JSON when asked."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=20)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception:
        return None
