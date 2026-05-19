"""Redis pub/sub abstraction with in-memory fallback when Redis unavailable."""
from __future__ import annotations

import json
import logging
import threading
from collections import defaultdict
from typing import Callable

from apps.core.redis_cache import get_redis_client, log_redis_fallback_once, redis_pubsub_available

logger = logging.getLogger("nptte.redis_bus")

_local_subscribers: dict[str, list[Callable[[str, dict], None]]] = defaultdict(list)
_local_lock = threading.Lock()
_memory_pubsub: "InMemoryPubSub | None" = None


class BasePubSub:
    def publish(self, channel: str, message: dict) -> bool:
        raise NotImplementedError

    def subscribe(self, channel: str, handler: Callable[[str, dict], None]) -> None:
        raise NotImplementedError


class InMemoryPubSub(BasePubSub):
    """Local fallback — no Redis required."""

    def publish(self, channel: str, message: dict) -> bool:
        with _local_lock:
            handlers = list(_local_subscribers.get(channel, []))
        for handler in handlers:
            try:
                handler(channel, message)
            except Exception as exc:
                logger.debug("In-memory pub/sub handler error: %s", exc)
        return True

    def subscribe(self, channel: str, handler: Callable[[str, dict], None]) -> None:
        with _local_lock:
            _local_subscribers[channel].append(handler)


def _memory_fallback() -> InMemoryPubSub:
    global _memory_pubsub
    if _memory_pubsub is None:
        _memory_pubsub = InMemoryPubSub()
    return _memory_pubsub


class RedisPubSub(BasePubSub):
    """Redis pub/sub when a Redis client is available."""

    def publish(self, channel: str, message: dict) -> bool:
        client = get_redis_client(write=True)
        if client is None:
            return _memory_fallback().publish(channel, message)
        try:
            client.publish(channel, json.dumps(message, default=str))
            return True
        except Exception as exc:
            log_redis_fallback_once(
                "Redis publish failed, using in-memory pub/sub fallback: %s", exc
            )
            return _memory_fallback().publish(channel, message)

    def subscribe(self, channel: str, handler: Callable[[str, dict], None]) -> None:
        _memory_fallback().subscribe(channel, handler)


def get_pubsub() -> BasePubSub:
    if redis_pubsub_available():
        return RedisPubSub()
    return _memory_fallback()


def publish_channel(channel: str, message: dict) -> bool:
    return get_pubsub().publish(channel, message)
