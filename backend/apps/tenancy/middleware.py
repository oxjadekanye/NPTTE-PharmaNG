"""Phase 14 — attach active organisation context to each request."""
from apps.tenancy.services.tenant import resolve_request_organisation_id


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.nptte_organisation_id = resolve_request_organisation_id(request)
        return self.get_response(request)
