"""Phase 19 — explorer HTTP API."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.explorer.constants import ENTITY_TYPES
from apps.explorer.services.access_control import (
    assert_explorer_access,
    assert_regional_explorer_access,
    aggregate_requires_regulator,
    is_aggregate_id,
)
from apps.explorer.services.entity_resolution import resolve_entity
from apps.explorer.services.execute_action import execute_explorer_action
from apps.explorer.services.payloads import (
    build_evidence_entries,
    build_explorer_bundle,
    build_timeline_entries,
    get_access_handles,
    list_operational_actions,
)
from apps.explorer.services import risk_breakdown
from apps.operations.models import RegulatorOperationalHistory
from apps.tenancy.services.tenant import log_tenant_access_denied


def _audit_regulator_explore(*, user, entity_type: str, entity_id: str) -> None:
    if not (is_regulator_user(user) or user.is_superuser):
        return
    try:
        RegulatorOperationalHistory.objects.create(
            action_type="explorer_detail",
            actor=user,
            summary=f"Explorer {entity_type}/{entity_id}"[:2000],
            entity_type=entity_type,
            entity_id=None,
            organisation=None,
        )
    except Exception:
        pass


def _check_explorer_access(request, entity_type: str, entity_id: str) -> tuple[bool, str]:
    if entity_type not in ENTITY_TYPES:
        return False, "invalid_entity_type"

    if entity_type == "regional_risk":
        return assert_regional_explorer_access(request, region_state=entity_id)

    if is_aggregate_id(entity_id):
        if aggregate_requires_regulator(entity_id) and not (
            is_regulator_user(request.user) or request.user.is_superuser
        ):
            log_tenant_access_denied(
                request,
                detail=f"explorer aggregate denied: {entity_type}/{entity_id}",
            )
            return False, "aggregate_regulator_only"
        return True, ""

    handles = get_access_handles(entity_type, entity_id)
    if handles.get("invalid_uuid"):
        return False, "invalid_entity_id"
    if handles.get("missing"):
        return False, "not_found"

    if entity_type == "notification":
        ok, reason = assert_explorer_access(
            request,
            entity_type=entity_type,
            entity_id=entity_id,
            related_organisation_id=handles.get("organisation_id"),
            notification_recipient_id=handles.get("notification_recipient_id"),
        )
        return ok, reason

    if entity_type in ("enforcement_case", "incident", "national_risk", "intelligence_signal"):
        if not handles.get("organisation_id"):
            if is_regulator_user(request.user) or request.user.is_superuser:
                return True, ""
            log_tenant_access_denied(
                request,
                detail=f"explorer national-scope entity denied: {entity_type}/{entity_id}",
            )
            return False, "regulator_required"

    ok, reason = assert_explorer_access(
        request,
        entity_type=entity_type,
        entity_id=entity_id,
        related_organisation_id=handles.get("organisation_id"),
    )
    return ok, reason


class ExplorerResolveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entity_type = request.query_params.get("type", "").strip()
        entity_id = request.query_params.get("id", "").strip()
        if not entity_type or not entity_id:
            return api_response(message="type and id required", status_code=400)
        if entity_type not in ENTITY_TYPES:
            return api_response(message="invalid entity type", status_code=400)
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403)
        data = resolve_entity(entity_type=entity_type, entity_id=entity_id)
        return api_response(data=data, message="Resolved")


class ExplorerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        bundle = build_explorer_bundle(request, entity_type, entity_id)
        _audit_regulator_explore(user=request.user, entity_type=entity_type, entity_id=entity_id)
        return api_response(data=bundle, message="Explorer detail")


class ExplorerRelatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        bundle = build_explorer_bundle(request, entity_type, entity_id)
        return api_response(data={"related_entities": bundle.get("related_entities")}, message="Related")


class ExplorerTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        bundle = build_explorer_bundle(request, entity_type, entity_id)
        tl = bundle.get("timeline") or build_timeline_entries(entity_type, entity_id)
        return api_response(data={"timeline": tl}, message="Timeline")


class ExplorerEvidenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        bundle = build_explorer_bundle(request, entity_type, entity_id)
        ev = bundle.get("evidence") or build_evidence_entries(entity_type, entity_id)
        return api_response(data={"evidence": ev}, message="Evidence")


class ExplorerActionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        actions = list_operational_actions(entity_type, entity_id)
        return api_response(data={"actions": actions}, message="Actions")


class ExplorerRiskBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        if is_aggregate_id(entity_id) and entity_id == "national-risk-current":
            return api_response(data=risk_breakdown.national_risk_breakdown(), message="Risk breakdown")
        if entity_type == "regional_risk":
            return api_response(
                data=risk_breakdown.regional_risk_breakdown(entity_id),
                message="Risk breakdown",
            )
        bundle = build_explorer_bundle(request, entity_type, entity_id)
        return api_response(data=bundle.get("risk_explanation") or {}, message="Risk breakdown")


class ExplorerExecuteActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, entity_type, entity_id):
        if not (is_regulator_user(request.user) or request.user.is_superuser):
            return api_response(message="Regulator access required", status_code=403)
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        action_id = request.data.get("action_id", "")
        result = execute_explorer_action(
            request=request,
            entity_type=entity_type,
            entity_id=entity_id,
            action_id=action_id,
            payload=request.data,
        )
        if not result.get("ok"):
            return api_response(data=result, message=result.get("error", "failed"), status_code=400)
        return api_response(data=result, message="Action executed", status_code=201)
