"""Audit logging service for API and security events."""
from __future__ import annotations
import uuid
from typing import Any

from apps.audit.models import AuditLog


def log_api_action(
    *,
    request=None,
    actor=None,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | str | None = None,
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    """Create an append-only audit log entry."""
    if request is not None:
        actor = actor or getattr(request, "user", None)
        if actor is not None and not getattr(actor, "is_authenticated", False):
            actor = None
        ip_address = _client_ip(request)
        user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:512]
        path = request.path
        method = request.method
    else:
        ip_address = None
        user_agent = ""
        path = ""
        method = ""

    if entity_id is None:
        entity_id = uuid.uuid4()

    payload = after_state or {}
    if request is not None:
        payload = {
            **payload,
            "http_method": method,
            "path": path,
        }

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id if isinstance(entity_id, uuid.UUID) else uuid.UUID(str(entity_id)),
        ip_address=ip_address,
        user_agent=user_agent,
        before_state=before_state or {},
        after_state=payload,
        metadata=metadata or {},
    )


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
