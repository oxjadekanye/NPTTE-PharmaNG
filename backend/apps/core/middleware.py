"""API middleware for automatic audit logging."""
from apps.audit.services import log_api_action


class APIAuditMiddleware:
    """
    Log mutating API requests under /api/v1/ after the view completes.

    Skips health checks and schema endpoints to reduce noise.
    """

    MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
    SKIP_PATH_PREFIXES = (
        "/api/v1/health/",
        "/api/schema/",
        "/api/docs/",
        "/api/redoc/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if self._should_audit(request, response):
            try:
                log_api_action(
                    request=request,
                    action=f"api.{request.method.lower()}",
                    entity_type="api_request",
                    entity_id=None,
                    after_state={
                        "status_code": response.status_code,
                        "view": getattr(request.resolver_match, "view_name", ""),
                    },
                )
            except Exception:
                pass  # Never block responses due to audit failures
        return response

    def _should_audit(self, request, response) -> bool:
        if request.method not in self.MUTATING_METHODS:
            return False
        if not request.path.startswith("/api/v1/"):
            return False
        if any(request.path.startswith(p) for p in self.SKIP_PATH_PREFIXES):
            return False
        if response.status_code >= 500:
            return False
        return True
