"""Phase 10 — API keys, scopes, and audit for public ecosystem integrations."""
from django.conf import settings
from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.organisations.models import Organisation


class ApiDeveloperKey(NPTTEBaseModel):
    name = models.CharField(max_length=128)
    key_prefix = models.CharField(max_length=16, db_index=True)
    key_hash = models.CharField(max_length=128, unique=True)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="api_keys",
        null=True,
        blank=True,
    )
    scopes = models.JSONField(default=list, blank=True, help_text="e.g. verify.read, traceability.write")
    is_active_key = models.BooleanField(default=True, db_index=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class ApiRequestAudit(NPTTEBaseModel):
    api_key = models.ForeignKey(
        ApiDeveloperKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_audits",
    )
    path = models.CharField(max_length=255, db_index=True)
    method = models.CharField(max_length=16)
    status_code = models.PositiveSmallIntegerField(default=200)
    client_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
