"""Phase 20A.3 — production Redis cache backend and safe pub/sub."""
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.core.redis_bus import RedisPubSub, publish_channel
from apps.core.redis_cache import (
    cache_delete_pattern,
    get_redis_client,
    is_redis_cache_backend,
    redis_pubsub_available,
)


class Phase20A3RedisCacheTests(TestCase):
    def test_locmem_is_not_redis_backend(self):
        self.assertFalse(is_redis_cache_backend())

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/1",
            }
        }
    )
    def test_redis_backend_detected(self):
        self.assertTrue(is_redis_cache_backend())

    def test_delete_pattern_noop_on_locmem(self):
        self.assertFalse(cache_delete_pattern("nptte:explorer:*"))

    @override_settings(REDIS_URL="redis://127.0.0.1:6379/0")
    def test_redis_pubsub_available_with_url_only(self):
        self.assertTrue(redis_pubsub_available())

    @override_settings(REDIS_URL="")
    def test_redis_pubsub_unavailable_without_url(self):
        self.assertFalse(redis_pubsub_available())

    @patch("apps.core.redis_bus.get_redis_client")
    def test_publish_never_touches_cache_client(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        with override_settings(REDIS_URL="redis://127.0.0.1:6379/0"):
            ok = RedisPubSub().publish("test:ch", {"ok": True})
        self.assertTrue(ok)
        mock_client.publish.assert_called_once()
        mock_get_client.assert_called_once()

    @patch("apps.core.redis_bus.get_redis_client", return_value=None)
    def test_publish_falls_back_without_client(self, _mock):
        received = []

        def handler(channel, message):
            received.append((channel, message))

        from apps.core.redis_bus import InMemoryPubSub

        pubsub = InMemoryPubSub()
        pubsub.subscribe("fallback:ch", handler)
        with override_settings(REDIS_URL="redis://127.0.0.1:6379/0"):
            publish_channel("fallback:ch", {"x": 1})
        self.assertEqual(len(received), 1)

    def test_get_redis_client_none_without_redis(self):
        self.assertIsNone(get_redis_client())
