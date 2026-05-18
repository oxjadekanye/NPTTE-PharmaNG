"""Web/mobile push notification foundation (no production provider required)."""
from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model

from apps.integrations.models import ProviderHealthStatus, PushDeviceRegistration
from apps.integrations.providers.email import _upsert_provider_health

logger = logging.getLogger("nptte.integrations.push")
User = get_user_model()


def register_push_device(*, user, platform: str = "web", endpoint: str = "", keys: dict | None = None) -> PushDeviceRegistration:
    reg, _ = PushDeviceRegistration.objects.update_or_create(
        user=user,
        platform=platform,
        endpoint=endpoint or f"device-{user.id}",
        defaults={"subscription_keys": keys or {}, "is_active": True},
    )
    return reg


def send_push_to_user(*, user, title: str, body: str, data: dict | None = None) -> int:
    """Mock dispatch — logs and returns device count."""
    devices = PushDeviceRegistration.objects.filter(user=user, is_active=True)
    count = devices.count()
    for device in devices:
        logger.info("Push [%s] %s → %s: %s", device.platform, title, device.endpoint[:40], body[:60])
    _upsert_provider_health(ProviderHealthStatus.PROVIDER_PUSH, "web_push_mock", ProviderHealthStatus.STATUS_HEALTHY, "Mock push active")
    return count


def push_health() -> tuple[str, str]:
    active = PushDeviceRegistration.objects.filter(is_active=True).count()
    return ProviderHealthStatus.STATUS_HEALTHY, f"{active} active device registrations"
