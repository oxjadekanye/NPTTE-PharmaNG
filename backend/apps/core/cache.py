"""Cache abstraction — Redis-ready without hard dependency."""
from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.core.cache import cache


def cache_get(key: str, default=None):
  if not getattr(settings, "REDIS_URL", ""):
    return default
  return cache.get(key, default)


def cache_set(key: str, value: Any, timeout: int = 300) -> None:
  if not getattr(settings, "REDIS_URL", ""):
    return
  cache.set(key, value, timeout)


def dashboard_cache_key(name: str, **params) -> str:
  suffix = hashlib_hex(json.dumps(params, sort_keys=True, default=str))
  return f"nptte:dashboard:{name}:{suffix}"


def hashlib_hex(data: str) -> str:
  import hashlib
  return hashlib.sha256(data.encode()).hexdigest()[:16]
