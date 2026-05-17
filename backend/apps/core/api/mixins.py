"""Reusable API view mixins."""
from apps.audit.services import log_api_action


class AuditLogViewMixin:
    """Explicit audit log on create/update/destroy beyond middleware."""

    audit_entity_type = "unknown"

    def _audit(self, request, action: str, instance=None, before=None, after=None):
        entity_id = getattr(instance, "id", None) if instance else None
        log_api_action(
            request=request,
            action=action,
            entity_type=self.audit_entity_type,
            entity_id=entity_id,
            before_state=before,
            after_state=after,
        )
