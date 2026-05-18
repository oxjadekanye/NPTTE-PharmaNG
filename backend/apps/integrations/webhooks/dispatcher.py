"""Outbound webhook dispatch with retry-ready delivery logs."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import urllib.error
import urllib.request

from django.utils import timezone

from apps.core.tasks import enqueue_task
from apps.integrations.models import ProviderHealthStatus, WebhookDeliveryLog, WebhookSubscription
from apps.integrations.providers.email import _upsert_provider_health

logger = logging.getLogger("nptte.integrations.webhooks")


def publish_integration_event(*, event_type: str, payload: dict, organisation=None) -> list[WebhookDeliveryLog]:
    """Publish event to all matching webhook subscriptions."""
    from django.db.models import Q

    qs = WebhookSubscription.objects.filter(is_active_subscription=True)
    if organisation:
        qs = qs.filter(Q(organisation=organisation) | Q(organisation__isnull=True))
    logs = []
    for sub in qs:
        if sub.subscribed_events and event_type not in sub.subscribed_events:
            continue
        logs.append(dispatch_webhook_event(subscription=sub, event_type=event_type, payload=payload))
    return logs


def dispatch_webhook_event(
    *, subscription: WebhookSubscription, event_type: str, payload: dict, async_delivery: bool = True
) -> WebhookDeliveryLog:
    log = WebhookDeliveryLog.objects.create(
        subscription=subscription,
        event_type=event_type,
        payload=payload,
        delivery_status="pending",
    )

    def _deliver():
        _attempt_delivery(log=log, subscription=subscription, event_type=event_type, payload=payload)

    if async_delivery:
        enqueue_task(f"webhook_{log.id}", _deliver)
    else:
        _deliver()
    return log


def _attempt_delivery(*, log: WebhookDeliveryLog, subscription: WebhookSubscription, event_type: str, payload: dict) -> None:
    body = json.dumps({"event": event_type, "payload": payload, "timestamp": timezone.now().isoformat()}).encode()
    headers = {"Content-Type": "application/json", "X-NPTTE-Event": event_type}
    if subscription.secret:
        sig = hmac.new(subscription.secret.encode(), body, hashlib.sha256).hexdigest()
        headers["X-NPTTE-Signature"] = sig
    req = urllib.request.Request(subscription.target_url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            log.http_status = resp.status
            log.delivery_status = "delivered" if resp.status < 400 else "failed"
    except urllib.error.URLError as exc:
        log.retry_count += 1
        log.delivery_status = "retry" if log.retry_count < 3 else "failed"
        log.error_message = str(exc)[:500]
        logger.warning("Webhook delivery failed: %s", exc)
    log.save(update_fields=["http_status", "delivery_status", "retry_count", "error_message", "updated_at"])
    status = ProviderHealthStatus.STATUS_HEALTHY if log.delivery_status == "delivered" else ProviderHealthStatus.STATUS_DEGRADED
    _upsert_provider_health(ProviderHealthStatus.PROVIDER_WEBHOOK, "outbound", status, log.delivery_status)
