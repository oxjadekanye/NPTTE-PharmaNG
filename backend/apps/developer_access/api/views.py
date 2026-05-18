from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.developer_access.models import ApiDeveloperKey, ApiRequestAudit
from apps.developer_access.services import create_api_key


class DeveloperPortalOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(
            data={
                "integrations": [
                    "manufacturers",
                    "pharmacies",
                    "hospitals",
                    "customs",
                    "distributors",
                    "gs1",
                ],
                "active_keys": ApiDeveloperKey.objects.filter(is_active_key=True).count(),
                "audit_events_24h": ApiRequestAudit.objects.count(),
            },
            message="Developer portal foundation",
        )


class DeveloperKeysView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        keys = ApiDeveloperKey.objects.order_by("-created_at")[:20]
        rows = [
            {"name": k.name, "prefix": k.key_prefix, "scopes": k.scopes, "active": k.is_active_key}
            for k in keys
        ]
        return api_response(data={"keys": rows}, message="API keys")

    def post(self, request):
        key, raw = create_api_key(
            name=request.data["name"],
            scopes=request.data.get("scopes"),
            actor=request.user,
        )
        return api_response(
            data={"key_prefix": key.key_prefix, "api_key_once": raw, "scopes": key.scopes},
            message="API key created — store secret now",
            status_code=201,
        )
