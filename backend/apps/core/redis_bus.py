"""Redis pub/sub abstraction with in-memory fallback when Redis unavailable."""
from __future__ import annotations

import json
import logging
import threading
from collections import defaultdict
from typing import Callable

from django.conf import settings

logger = logging.getLogger("nptte.redis_bus")

_local_subscribers: dict[str, list[Callable[[str, dict], None]]] = defaultdict(list)
_local_lock = threading.Lock()


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


class RedisPubSub(BasePubSub):
    """Redis pub/sub when REDIS_URL is configured."""

    def publish(self, channel: str, message: dict) -> bool:
        if not getattr(settings, "REDIS_URL", ""):
            return InMemoryPubSub().publish(channel, message)
        try:
            from django.core.cache import cache

            client = cache.client.get_client(write=True)
            client.publish(channel, json.dumps(message, default=str))
            return True
        except Exception as exc:
            logger.warning("Redis publish failed, using memory fallback: %s", exc)
            return InMemoryPubSub().publish(channel, message)

    def subscribe(self, channel: str, handler: Callable[[str, dict], None]) -> None:
        InMemoryPubSub().subscribe(channel, handler)


def get_pubsub() -> BasePubSub:
    if getattr(settings, "REDIS_URL", ""):
        return RedisPubSub()
    return InMemoryPubSub()


def publish_channel(channel: str, message: dict) -> bool:
    return get_pubsub().publish(channel, message)
