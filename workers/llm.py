"""Shared LLM client — BYOK (Bring Your Own Key) with any OpenAI-compatible provider."""

import os
import json

# Provider presets: name -> (base_url, default_model)
PROVIDERS = {
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.0-flash"),
    "groq": ("https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"),
    "openrouter": ("https://openrouter.ai/api/v1", "meta-llama/llama-3.3-70b-instruct:free"),
    "ollama": ("http://localhost:11434/v1", "llama3"),
}

_api_key = os.getenv("LLM_API_KEY", "")
_provider = os.getenv("LLM_PROVIDER", "").lower()
_base_url = os.getenv("LLM_BASE_URL", "")
_model = os.getenv("LLM_MODEL", "")

# Resolve config
if _provider in PROVIDERS:
    _default_url, _default_model = PROVIDERS[_provider]
    _base_url = _base_url or _default_url
    _model = _model or _default_model
elif _base_url:
    _model = _model or "default"
else:
    _base_url = PROVIDERS["openai"][0]
    _model = _model or "gpt-4o-mini"


def is_configured() -> bool:
    """Returns True if an LLM API key is available."""
    return bool(_api_key)


def complete(system_prompt: str, user_prompt: str) -> str:
    """Call LLM and return text response. Returns empty string on failure."""
    if not _api_key:
        return ""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=_api_key, base_url=_base_url)
        resp = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        print(f"[llm] error: {e}")
        return ""


def complete_json(system_prompt: str, user_prompt: str) -> dict:
    """Call LLM and parse JSON response. Returns empty dict on failure."""
    raw = complete(system_prompt + "\n\nRespond ONLY with valid JSON, no markdown.", user_prompt)
    if not raw:
        return {}
    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}
