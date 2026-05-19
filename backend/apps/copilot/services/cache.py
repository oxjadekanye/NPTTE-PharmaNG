"""Copilot response cache (10 min default)."""
from __future__ import annotations

import hashlib
import json

from django.core.cache import cache

from apps.copilot.constants import COPILOT_CACHE_TTL_SEC


def copilot_cache_key(
    *,
    mode: str,
    entity_type: str,
    entity_id: str,
    context_key: str = "",
    selected_ids: list[str] | None = None,
    user_id: str = "",
) -> str:
    ids_part = ",".join(sorted(str(i) for i in (selected_ids or [])))
    raw = f"{mode}:{context_key}:{entity_type}:{entity_id}:{ids_part}:{user_id}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"nptte:copilot:{digest}"


def get_cached_copilot(key: str) -> dict | None:
    val = cache.get(key)
    return val if isinstance(val, dict) else None


def set_cached_copilot(key: str, payload: dict, ttl: int = COPILOT_CACHE_TTL_SEC) -> None:
    cache.set(key, payload, timeout=ttl)
