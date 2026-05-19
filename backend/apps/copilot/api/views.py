"""Phase 20B — sovereign AI copilot APIs (on-demand only)."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.copilot.services.reasoning import run_copilot_reasoning


def _parse_body(request) -> dict:
    data = request.data if isinstance(request.data, dict) else {}
    selected = data.get("selected_record_ids") or data.get("record_ids") or []
    if not isinstance(selected, list):
        selected = []
    return {
        "entity_type": (data.get("entity_type") or "").strip(),
        "entity_id": (data.get("entity_id") or "").strip(),
        "context_key": (data.get("context_key") or "").strip(),
        "prompt_mode": (data.get("prompt_mode") or "").strip(),
        "user_question": data.get("user_question"),
        "selected_record_ids": [str(x) for x in selected if x],
    }


class CopilotBaseView(APIView):
    permission_classes = [IsAuthenticated]
    mode: str = ""

    def post(self, request):
        if not (is_regulator_user(request.user) or request.user.is_superuser):
            return api_response(message="regulator_only", status_code=403)

        body = _parse_body(request)
        mode = body["prompt_mode"] or self.mode
        if not mode:
            return api_response(message="prompt_mode required", status_code=400)

        if not body["context_key"] and not (body["entity_type"] and body["entity_id"]):
            return api_response(message="entity_type/entity_id or context_key required", status_code=400)

        payload, reason = run_copilot_reasoning(
            request=request,
            mode=mode,
            entity_type=body["entity_type"] or None,
            entity_id=body["entity_id"] or None,
            context_key=body["context_key"] or None,
            selected_record_ids=body["selected_record_ids"] or None,
            user_question=body["user_question"],
        )
        if payload is None:
            status = 403 if reason in ("aggregate_regulator_only", "authentication_required", "regulator_only") else 404
            return api_response(message=reason or "access_denied", status_code=status)

        return api_response(data=payload, message="Copilot response")


class CopilotExplainRiskView(CopilotBaseView):
    mode = "explain_risk"


class CopilotGenerateBriefingView(CopilotBaseView):
    mode = "generate_briefing"


class CopilotRecommendActionsView(CopilotBaseView):
    mode = "recommend_actions"


class CopilotSummariseInvestigationView(CopilotBaseView):
    mode = "summarise_investigation"


class CopilotDraftEnforcementNoteView(CopilotBaseView):
    mode = "draft_enforcement_note"


class CopilotExecutiveBriefingView(CopilotBaseView):
    """National executive briefing — uses national_status context."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (is_regulator_user(request.user) or request.user.is_superuser):
            return api_response(message="regulator_only", status_code=403)
        body = _parse_body(request)
        payload, reason = run_copilot_reasoning(
            request=request,
            mode="executive_briefing",
            context_key=body["context_key"] or "national_status",
            user_question=body["user_question"],
        )
        if payload is None:
            return api_response(message=reason or "access_denied", status_code=403)
        return api_response(data=payload, message="Executive briefing")
