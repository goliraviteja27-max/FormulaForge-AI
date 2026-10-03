from __future__ import annotations

import json
import os
import re

import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


def health() -> dict:
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=4)
        response.raise_for_status()
        names = [model.get("name", "") for model in response.json().get("models", [])]
        return {"online": True, "model": OLLAMA_MODEL, "available_models": names}
    except requests.RequestException as error:
        return {"online": False, "model": OLLAMA_MODEL, "error": str(error)}


def generate_json(prompt: str) -> dict:
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0.15, "num_predict": 5000}},
        timeout=240,
    )
    response.raise_for_status()
    content = response.json().get("response", "{}")
    cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.IGNORECASE).strip()
    return json.loads(cleaned)


def generate_text(prompt: str) -> str:
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.2, "num_predict": 900}},
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()
