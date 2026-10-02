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
import re
from typing import Optional, Tuple

import httpx


def clean_thinking_tags(text: str) -> str:
    """Completely strip internal model reasoning chains (<think>, <thought>)."""
    if not text:
        return ""

    cleaned = text

    # 1. Strip complete <think>...</think> and <thought>...</thought> blocks
    cleaned = re.sub(
        r"<(?:think|thought)>.*?</(?:think|thought)>",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # 2. Handle cases where <think> opened and closed before the real answer
    if "</think>" in cleaned.lower():
        parts = re.split(r"</think>", cleaned, flags=re.IGNORECASE)
        cleaned = parts[-1]
    elif "</thought>" in cleaned.lower():
        parts = re.split(r"</thought>", cleaned, flags=re.IGNORECASE)
        cleaned = parts[-1]

    # 3. Strip any residual unclosed opening tags
    cleaned = re.sub(r"<(?:think|thought)>\s*", "", cleaned, flags=re.IGNORECASE)

    # 4. Strip conversational 'Thinking Process:' markers
    cleaned = re.sub(
        r"^(?:thinking|thought)\s+process:\s*.*?\n\n",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE,
    )

    return cleaned.strip()


def generate_with_local_llm(
    prompt: str, model: Optional[str] = None
) -> Tuple[Optional[str], Optional[Exception]]:
    resolved_model = (
        model.strip() if model and model.strip() else os.getenv("LOCAL_LLM_MODEL", "Swift-1.5-Qwen3.8-27B-GSQ-RCO")
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
            timeout=180.0,
        )
        res.raise_for_status()
        data = res.json()
        choices = data.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            msg = choices[0].get("message", {})
            content = msg.get("content")
            if content and str(content).strip():
                sanitized = clean_thinking_tags(str(content).strip())
                if sanitized:
                    return sanitized, None
    except Exception as exc:
        last_error = exc

    # Fallback 1: llama.cpp native completion endpoint (/completion)
    try:
        res = httpx.post(
            f"{local_llm_url}/completion",
            json={"prompt": prompt, "temperature": 0.2},
            timeout=180.0,
        )
        res.raise_for_status()
        data = res.json()
        content = data.get("content")
        if content and str(content).strip():
            sanitized = clean_thinking_tags(str(content))
            if sanitized:
                return sanitized, None
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
            timeout=180.0,
        )
        res.raise_for_status()
        data = res.json()
        response_val = data.get("response")
        if response_val and str(response_val).strip():
            sanitized = clean_thinking_tags(str(response_val))
            if sanitized:
                return sanitized, None
    except Exception as exc:
        last_error = exc

    return None, last_error
