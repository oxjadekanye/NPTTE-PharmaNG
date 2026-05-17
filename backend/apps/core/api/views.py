"""Core API views."""
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Service health probe for load balancers and Render."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False

        status_label = "healthy" if db_ok else "degraded"
        http_status = 200 if db_ok else 503
        return Response(
            {
                "status": status_label,
                "service": "nptte-backend",
                "version": "v1",
                "database": "connected" if db_ok else "unavailable",
            },
            status=http_status,
        )
