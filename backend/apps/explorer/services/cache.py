"""Phase 20A — Redis/Django cache for explorer payloads."""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Callable

from apps.core.redis_cache import cache_delete_pattern, cache_get_safe, cache_set_safe

logger = logging.getLogger("nptte.explorer.cache")

TTL_NATIONAL_RISK = 90
TTL_TIMELINE = 45
TTL_ENFORCEMENT = 90
TTL_NARRATIVE = 120
TTL_DEFAULT = 60
TTL_OVERVIEW = 90
TTL_AGGREGATE = 90
TTL_CONTEXT_SUMMARY = 120

PREFIX = "nptte:explorer:v20a:"


def _slug(value: str, max_len: int = 64) -> str:
    return (value or "unknown").replace(":", "_")[:max_len]


def _cache_key(*, scope: str, entity_type: str, entity_id: str, user_id: str, org_scope: str = "") -> str:
    raw = f"{user_id}:{org_scope}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{PREFIX}{scope}:{_slug(entity_type)}:{_slug(entity_id)}:{digest}"


def get_cached(key: str) -> Any | None:
    return cache_get_safe(key)


def set_cached(key: str, value: Any, ttl: int) -> None:
    cache_set_safe(key, value, ttl)


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
    """Targeted invalidation for one entity across scopes."""
    et, eid = _slug(entity_type), _slug(entity_id)
    for scope in ("overview", "detail", "risk", "timeline", "evidence", "related", "context"):
        cache_delete_pattern(f"{PREFIX}{scope}:{et}:{eid}:*")


def invalidate_context(context_key: str) -> None:
    key = _slug(context_key.replace("-", "_"))
    cache_delete_pattern(f"{PREFIX}context:{key}*")
    cache_delete_pattern(f"{PREFIX}context-summary:{key}*")
    cache_delete_pattern(f"{PREFIX}context-records:{key}*")


def invalidate_scope(scope: str) -> None:
    cache_delete_pattern(f"{PREFIX}{scope}:*")


def invalidate_national() -> None:
    """Broad invalidation — use sparingly (e.g. full reseed)."""
    for scope in ("overview", "detail", "risk", "aggregate", "timeline", "context-summary"):
        invalidate_scope(scope)


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
