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
    ApiRequestAudit.objects.create(
        api_key=api_key,
        path=path,
        method=method,
        status_code=status_code,
        client_ip=client_ip,
    )
