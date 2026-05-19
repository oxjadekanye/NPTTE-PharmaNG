"""Cache abstraction — uses configured Django cache backend (Redis or LocMem)."""
from __future__ import annotations

import json
from typing import Any

from apps.core.redis_cache import cache_get_safe, cache_set_safe


def cache_get(key: str, default=None):
    return cache_get_safe(key, default)


def cache_set(key: str, value: Any, timeout: int = 300) -> None:
    cache_set_safe(key, value, timeout)


def dashboard_cache_key(name: str, **params) -> str:
    suffix = hashlib_hex(json.dumps(params, sort_keys=True, default=str))
    return f"nptte:dashboard:{name}:{suffix}"


def hashlib_hex(data: str) -> str:
    import hashlib

    return hashlib.sha256(data.encode()).hexdigest()[:16]
