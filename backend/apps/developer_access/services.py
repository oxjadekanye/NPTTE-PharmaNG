"""API key provisioning (foundation for public ecosystem)."""
from __future__ import annotations

import hashlib
import secrets

from apps.developer_access.models import ApiDeveloperKey, ApiRequestAudit


def create_api_key(*, name: str, organisation=None, scopes: list | None = None, actor=None) -> tuple[ApiDeveloperKey, str]:
    raw = f"nptte_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    prefix = raw[:12]
    key = ApiDeveloperKey.objects.create(
        name=name,
        key_prefix=prefix,
        key_hash=key_hash,
        organisation=organisation,
        scopes=scopes or ["verify.read"],
        created_by=actor,
    )
    return key, raw


def log_api_request(*, api_key, path: str, method: str, status_code: int, client_ip=None):
    from django.utils import timezone

    ApiRequestAudit.objects.create(
        api_key=api_key,
        path=path,
        method=method,
        status_code=status_code,
        client_ip=client_ip,
    )
    if api_key:
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=["last_used_at", "updated_at"])


def revoke_api_key(*, key: ApiDeveloperKey, actor=None) -> ApiDeveloperKey:
    key.is_active_key = False
    key.save(update_fields=["is_active_key", "updated_at"])
    log_api_request(api_key=key, path="/keys/revoke/", method="POST", status_code=200)
    return key


def rotate_api_key(*, key: ApiDeveloperKey, actor=None) -> tuple[ApiDeveloperKey, str]:
    revoke_api_key(key=key, actor=actor)
    return create_api_key(
        name=f"{key.name} (rotated)",
        organisation=key.organisation,
        scopes=key.scopes,
        actor=actor,
    )
