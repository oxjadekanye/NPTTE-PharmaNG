"""Strip secrets and oversized payloads before LLM prompts."""
from __future__ import annotations

import copy
import re
from typing import Any

SECRET_KEYS = frozenset(
    {
        "password",
        "secret",
        "api_key",
        "token",
        "authorization",
        "credential",
        "private_key",
    }
)

MAX_JSON_CHARS = 12_000


def _scrub_value(key: str, value: Any) -> Any:
    lk = key.lower()
    if any(s in lk for s in SECRET_KEYS):
        return "[redacted]"
    return value


def sanitize_context(data: dict | None) -> dict:
    if not data:
        return {}
    out = copy.deepcopy(data)
    _walk(out)
    text = str(out)
    if len(text) > MAX_JSON_CHARS:
        out["_truncated"] = True
        if isinstance(out.get("records"), list):
            out["records"] = out["records"][:15]
        if isinstance(out.get("records"), dict) and isinstance(out["records"].get("items"), list):
            out["records"]["items"] = out["records"]["items"][:15]
    return out


def _walk(node: Any, parent_key: str = "") -> None:
    if isinstance(node, dict):
        for k in list(node.keys()):
            node[k] = _scrub_value(k, node[k])
            _walk(node[k], k)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, (dict, list)):
                _walk(item, parent_key)


def sanitize_user_question(question: str | None) -> str:
    if not question:
        return ""
    q = re.sub(r"\s+", " ", str(question).strip())[:2000]
    return q
