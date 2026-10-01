"""Shared local-LLM generation helper.

Sends a prompt to the configured local LLM service, trying several
endpoint formats in order:
  1. OpenAI-compatible ``/v1/chat/completions``
  2. llama.cpp native ``/completion``
  3. Ollama ``/api/generate``

Returns ``(content, last_error)`` where ``content`` is the generated
text (or ``None`` if every endpoint failed) and ``last_error`` is the
most recent exception (or ``None``).
"""

import os
from typing import Optional, Tuple

import httpx


def generate_with_local_llm(
    prompt: str, model: Optional[str] = None
) -> Tuple[Optional[str], Optional[Exception]]:
    resolved_model = (
        model.strip() if model and model.strip() else os.getenv("LOCAL_LLM_MODEL", "Qwythos-9B")
    )
    local_llm_url = os.getenv(
        "LOCAL_LLM_URL", "http://host.docker.internal:8080"
    ).rstrip("/")

    last_error: Optional[Exception] = None

    # Primary: OpenAI format (/v1/chat/completions)
    try:
        res = httpx.post(
            f"{local_llm_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=120.0,
        )
        res.raise_for_status()
        data = res.json()
        choices = data.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            msg = choices[0].get("message", {})
            content = msg.get("content")
            if not content or not str(content).strip():
                content = msg.get("reasoning_content")
            if content and str(content).strip():
                return str(content).strip(), None
    except Exception as exc:
        last_error = exc

    # Fallback 1: llama.cpp native completion endpoint (/completion)
    try:
        res = httpx.post(
            f"{local_llm_url}/completion",
            json={"prompt": prompt, "temperature": 0.2},
            timeout=120.0,
        )
        res.raise_for_status()
        data = res.json()
        content = data.get("content")
        if content and str(content).strip():
            return str(content).strip(), None
    except Exception as exc:
        last_error = exc

    # Fallback 2: Ollama format (/api/generate)
    try:
        res = httpx.post(
            f"{local_llm_url}/api/generate",
            json={
                "model": resolved_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120.0,
        )
        res.raise_for_status()
        data = res.json()
        response_val = data.get("response")
        if response_val and str(response_val).strip():
            return str(response_val).strip(), None
    except Exception as exc:
        last_error = exc

    return None, last_error
