"""OpenAI provider adapter with timeout and JSON parsing."""
from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any

from apps.copilot.constants import OPENAI_TIMEOUT_SEC

logger = logging.getLogger("nptte.copilot.provider")


def openai_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def call_openai_json(*, system: str, user_prompt: str, timeout_sec: int = OPENAI_TIMEOUT_SEC) -> dict | None:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

        def _call():
            return client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=900,
                timeout=timeout_sec,
                response_format={"type": "json_object"},
            )

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_call)
            resp = future.result(timeout=timeout_sec + 2)
        text = (resp.choices[0].message.content or "").strip()
        return _parse_json(text)
    except (FuturesTimeout, Exception) as exc:
        logger.warning("OpenAI copilot call failed: %s", exc)
        return None


def _parse_json(text: str) -> dict:
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text.strip())
    return data if isinstance(data, dict) else {}
