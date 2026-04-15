from __future__ import annotations

import json
from typing import Any

import httpx

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def chat_json(*, api_key: str, model: str, system: str, user: Any, temperature: float = 0.2, max_tokens: int = 900) -> dict:
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
    return json.loads(text)
