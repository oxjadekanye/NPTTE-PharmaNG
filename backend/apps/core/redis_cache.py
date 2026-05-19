"""Redis cache backend detection and safe client access."""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("nptte.redis_cache")

REDIS_CACHE_BACKEND = "django_redis.cache.RedisCache"

_fallback_warned = False


def is_redis_cache_backend(cache_alias: str = "default") -> bool:
    """True when Django's default cache is django-redis (not LocMem or similar)."""
    caches = getattr(settings, "CACHES", {})
    backend = caches.get(cache_alias, {}).get("BACKEND", "")
    return backend == REDIS_CACHE_BACKEND or backend.endswith(".RedisCache")


def log_redis_fallback_once(message: str, *args: Any) -> None:
    """Emit a single warning; subsequent fallbacks log at debug only."""
    global _fallback_warned
    if _fallback_warned:
        logger.debug(message, *args)
        return
    _fallback_warned = True
    logger.warning(message, *args)


def get_redis_client(*, write: bool = True):
    """
    Return a Redis client for pub/sub or direct operations.

    Uses django-redis when the cache backend is Redis; otherwise opens a
    one-off client from REDIS_URL when set (misconfigured cache on Render).
    Never touches cache.client on non-Redis backends.
    """
    if is_redis_cache_backend():
        from django_redis import get_redis_connection

        return get_redis_connection("default", write=write)

    url = getattr(settings, "REDIS_URL", "") or ""
    if not url:
        return None
    try:
        import redis

        return redis.from_url(url, decode_responses=True)
    except Exception as exc:
        log_redis_fallback_once("Could not create Redis client from REDIS_URL: %s", exc)
        return None


def redis_pubsub_available() -> bool:
    """Whether Redis pub/sub should be attempted (configured backend or URL)."""
    if is_redis_cache_backend():
        return True
    return bool(getattr(settings, "REDIS_URL", "") or "")


def cache_delete_pattern(pattern: str, cache_alias: str = "default") -> bool:
    """Pattern delete via django-redis; no-op on non-Redis backends."""
    if not is_redis_cache_backend():
        return False
    try:
        from django.core.cache import caches

        c = caches[cache_alias]
        if hasattr(c, "delete_pattern"):
            c.delete_pattern(pattern)
            return True
    except Exception as exc:
        logger.debug("cache delete_pattern failed for %s: %s", pattern, exc)
    return False


def cache_get_safe(key: str, default=None):
    try:
        return cache.get(key, default)
    except Exception as exc:
        logger.debug("cache get failed for %s: %s", key, exc)
        return default


def cache_set_safe(key: str, value: Any, timeout: int = 300) -> None:
    try:
        cache.set(key, value, timeout)
    except Exception as exc:
        logger.debug("cache set failed for %s: %s", key, exc)
