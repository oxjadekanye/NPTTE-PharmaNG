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
        qs = NationalAlert.objects.select_related("organisation", "product").order_by("-created_at")
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
            org = a.organisation
            ev = a.evidence_payload if isinstance(a.evidence_payload, dict) else {}
            city = (org.city if org else "") or str(ev.get("city") or "")
            entry = {
                "id": str(a.id),
                "alert_type": a.alert_type,
                "title": a.title,
                "description": a.description,
                "severity": a.severity,
                "priority": a.risk_level,
                "state": a.state or str(ev.get("state") or ""),
                "unread": True,
                "created_at": a.created_at.isoformat(),
                "detected_at": str(ev.get("detected_at") or a.created_at.isoformat()),
                "organisation_name": (org.legal_name if org else "") or str(ev.get("organisation_name") or ""),
                "address_line": (org.address_line_1 if org else "") or str(ev.get("address") or ""),
                "address_line_2": org.address_line_2 if org else "",
                "city": city,
                "lga": str(ev.get("lga") or (f"{city} LGA" if city else "")),
                "product_name": (a.product.name if a.product else "") or str(ev.get("product") or ""),
                "batch": str(ev.get("batch") or ""),
                "serial": str(ev.get("serial") or ""),
                "risk_explanation": a.description or "",
                "recommended_action": str(ev.get("recommended_action") or ""),
                "linked_task_id": str(ev.get("task_id") or ""),
                "linked_investigation_id": str(ev.get("investigation_id") or ""),
                "evidence_payload": ev,
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
