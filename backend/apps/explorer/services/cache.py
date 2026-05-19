"""Phase 20A — Redis/Django cache for explorer payloads."""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Callable

from django.core.cache import cache

logger = logging.getLogger("nptte.explorer.cache")

TTL_NATIONAL_RISK = 30
TTL_TIMELINE = 20
TTL_ENFORCEMENT = 60
TTL_NARRATIVE = 120
TTL_DEFAULT = 30
TTL_OVERVIEW = 25
TTL_AGGREGATE = 30

PREFIX = "nptte:explorer:v20a:"


def _cache_key(*, scope: str, entity_type: str, entity_id: str, user_id: str, org_scope: str = "") -> str:
    raw = f"{scope}:{entity_type}:{entity_id}:{user_id}:{org_scope}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:24]
    return f"{PREFIX}{scope}:{digest}"


def get_cached(key: str) -> Any | None:
    try:
        return cache.get(key)
    except Exception as exc:
        logger.debug("explorer cache get failed: %s", exc)
        return None


def set_cached(key: str, value: Any, ttl: int) -> None:
    try:
        cache.set(key, value, ttl)
    except Exception as exc:
        logger.debug("explorer cache set failed: %s", exc)


def cached_explorer(
    *,
    scope: str,
    entity_type: str,
    entity_id: str,
    user_id: str,
    ttl: int,
    builder: Callable[[], Any],
    org_scope: str = "",
) -> Any:
    key = _cache_key(
        scope=scope,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        org_scope=org_scope,
    )
    hit = get_cached(key)
    if hit is not None:
        return hit
    value = builder()
    set_cached(key, value, ttl)
    return value


def invalidate_entity(entity_type: str, entity_id: str) -> None:
    """Best-effort pattern invalidation (django-redis supports delete_pattern)."""
    try:
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"{PREFIX}*{entity_type}*{entity_id}*")
        else:
            cache.delete_many([])
    except Exception as exc:
        logger.debug("explorer cache invalidate: %s", exc)


def invalidate_scope(scope: str) -> None:
    try:
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"{PREFIX}{scope}:*")
    except Exception:
        pass


def invalidate_national() -> None:
    invalidate_scope("overview")
    invalidate_scope("detail")
    invalidate_scope("risk")
    invalidate_scope("aggregate")
    invalidate_scope("timeline")


def ttl_for_scope(scope: str) -> int:
    if scope in ("risk", "overview") and "national" in scope:
        return TTL_NATIONAL_RISK
    if scope == "timeline":
        return TTL_TIMELINE
    if scope in ("detail", "actions") and "enforcement" in scope:
        return TTL_ENFORCEMENT
    if scope == "narrative":
        return TTL_NARRATIVE
    if scope == "aggregate":
        return TTL_AGGREGATE
    return TTL_DEFAULT
