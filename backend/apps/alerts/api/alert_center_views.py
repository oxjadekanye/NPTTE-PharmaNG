"""Phase 11 — national alert center aggregation."""
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.alerts.models import NationalAlert
from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user


class NationalAlertCenterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            return api_response(message="Regulator access required", status_code=403)
        priority = request.GET.get("priority")
        alert_type = request.GET.get("alert_type")
        qs = NationalAlert.objects.all().order_by("-created_at")
        if priority:
            from django.db.models import Q

            qs = qs.filter(Q(risk_level=priority) | Q(severity=priority))
        if alert_type:
            qs = qs.filter(alert_type=alert_type)
        rows = qs[:100]
        grouped: dict[str, list] = {}
        alerts = []
        for a in rows:
            key = a.alert_type or "general"
            entry = {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "title": a.title,
                "description": a.description,
                "severity": a.severity,
                "priority": a.risk_level,
                "state": a.state,
                "unread": True,
                "created_at": a.created_at.isoformat(),
                "actions": [{"label": "Open in explorer", "action": "open_explorer", "entity_type": "alert"}],
            }
            alerts.append(entry)
            grouped.setdefault(key, []).append(entry)
        return api_response(
            data={
                "alerts": alerts,
                "grouped": grouped,
                "unread_count": len(alerts),
                "polled_at": timezone.now().isoformat(),
            },
            message="National alert center",
        )
