"""Phase 19/20A — explorer HTTP API with caching and split payloads."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.explorer.constants import AGGREGATE_IDS, ENTITY_TYPES
from apps.explorer.services.access_control import (
    assert_explorer_access,
    assert_regional_explorer_access,
    aggregate_requires_regulator,
    is_aggregate_id,
)
from apps.core.perf import perf_span
from apps.explorer.services.cache import (
    TTL_CONTEXT_SUMMARY,
    TTL_ENFORCEMENT,
    TTL_NATIONAL_RISK,
    TTL_OVERVIEW,
    TTL_TIMELINE,
    cached_explorer,
)
from apps.explorer.services.context_aggregates import build_context_aggregate_bundle
from apps.explorer.services.context_router import resolve_context_route
from apps.explorer.services.context_summary import (
    build_context_records,
    build_context_summary,
)
from apps.explorer.services.staff import list_assignable_staff
from apps.explorer.services.entity_resolution import resolve_entity
from apps.explorer.services.execute_action import execute_explorer_action
from apps.explorer.services.invalidate import on_enforcement_mutation
from apps.explorer.services.overview import build_explorer_overview
from apps.explorer.services.pagination import paginate_list
from apps.explorer.services.payloads import (
    build_evidence_entries,
    build_explorer_bundle,
    build_graph_stub,
    build_timeline_entries,
    get_access_handles,
    list_operational_actions,
)
from apps.explorer.services import risk_breakdown
from apps.operations.models import RegulatorOperationalHistory
from apps.tenancy.services.tenant import get_active_organisation_id, log_tenant_access_denied


def _user_cache_id(request) -> str:
    return str(request.user.pk) if request.user.is_authenticated else "anon"


def _org_scope(request) -> str:
    oid = get_active_organisation_id(request)
    return str(oid) if oid else ""


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


def _page_params(request) -> tuple[int, int]:
    try:
        page = int(request.query_params.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(request.query_params.get("page_size", 25))
    except (TypeError, ValueError):
        page_size = 25
    return page, page_size


class ExplorerStaffView(APIView):
    """Assignable regulator staff for explorer workflows."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (is_regulator_user(request.user) or request.user.is_superuser):
            return api_response(message="Regulator access required", status_code=403)
        uid = _user_cache_id(request)

        def _build():
            return {"staff": list_assignable_staff()}

        data = cached_explorer(
            scope="staff",
            entity_type="regulator",
            entity_id="assignable",
            user_id=uid,
            ttl=300,
            org_scope="",
            builder=_build,
        )
        return api_response(data=data, message="Assignable staff")


class ExplorerContextBundleView(APIView):
    """Rich context-specific bundle for dashboard cards (cached)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context_key = request.query_params.get("context", "").strip()
        if not context_key:
            return api_response(message="context required", status_code=400)
        route = resolve_context_route(context_key=context_key, user=request.user)
        ok, reason = _check_explorer_access(request, route["entity_type"], route["entity_id"])
        if not ok:
            return api_response(message=reason, status_code=403)
        uid = _user_cache_id(request)
        org = _org_scope(request)

        def _build():
            if route["entity_id"] in AGGREGATE_IDS:
                return build_context_aggregate_bundle(aggregate_id=route["entity_id"], request=request)
            return build_explorer_bundle(request, route["entity_type"], route["entity_id"])

        data = cached_explorer(
            scope=f"context:{context_key}",
            entity_type=route["entity_type"],
            entity_id=route["entity_id"],
            user_id=uid,
            ttl=TTL_NATIONAL_RISK,
            org_scope=org,
            builder=_build,
        )
        data["route"] = route
        page, page_size = _page_params(request)
        if isinstance(data.get("records"), list):
            data["records"] = paginate_list(data["records"], page=page, page_size=page_size)
        return api_response(data=data, message="Context bundle")


class ExplorerContextRouteView(APIView):
    """Resolve dashboard context key to a concrete entity target."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context_key = request.query_params.get("context", "").strip()
        if not context_key:
            return api_response(message="context required", status_code=400)
        with perf_span(f"explorer.context-route:{context_key}"):
            route = resolve_context_route(context_key=context_key, user=request.user)
            ok, reason = _check_explorer_access(request, route["entity_type"], route["entity_id"])
            if not ok:
                return api_response(message=reason, status_code=403)
            return api_response(data=route, message="Context routed")


class ExplorerContextSummaryView(APIView):
    """Lightweight summary for instant drawer paint."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context_key = request.query_params.get("context", "").strip()
        if not context_key:
            return api_response(message="context required", status_code=400)
        route = resolve_context_route(context_key=context_key, user=request.user)
        ok, reason = _check_explorer_access(request, route["entity_type"], route["entity_id"])
        if not ok:
            return api_response(message=reason, status_code=403)
        uid = _user_cache_id(request)
        org = _org_scope(request)

        def _build():
            return build_context_summary(context_key=context_key, request=request)

        with perf_span(f"explorer.context-summary:{context_key}"):
            data = cached_explorer(
                scope="context-summary",
                entity_type="context",
                entity_id=context_key,
                user_id=uid,
                ttl=TTL_CONTEXT_SUMMARY,
                org_scope=org,
                builder=_build,
            )
            data["route"] = route
            return api_response(data=data, message="Context summary")


class ExplorerContextRecordsView(APIView):
    """Paginated records for a dashboard context."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context_key = request.query_params.get("context", "").strip()
        if not context_key:
            return api_response(message="context required", status_code=400)
        route = resolve_context_route(context_key=context_key, user=request.user)
        ok, reason = _check_explorer_access(request, route["entity_type"], route["entity_id"])
        if not ok:
            return api_response(message=reason, status_code=403)
        page, page_size = _page_params(request)
        uid = _user_cache_id(request)
        org = _org_scope(request)

        def _build():
            return build_context_records(
                context_key=context_key,
                request=request,
                page=page,
                page_size=page_size,
            )

        with perf_span(f"explorer.context-records:{context_key}"):
            data = cached_explorer(
                scope=f"context-records:{page}:{page_size}",
                entity_type="context",
                entity_id=context_key,
                user_id=uid,
                ttl=TTL_NATIONAL_RISK,
                org_scope=org,
                builder=_build,
            )
            return api_response(data=data, message="Context records")


class ExplorerContextActionsView(APIView):
    """Action metadata only for a dashboard context."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context_key = request.query_params.get("context", "").strip()
        if not context_key:
            return api_response(message="context required", status_code=400)
        route = resolve_context_route(context_key=context_key, user=request.user)
        ok, reason = _check_explorer_access(request, route["entity_type"], route["entity_id"])
        if not ok:
            return api_response(message=reason, status_code=403)
        actions = list_operational_actions(route["entity_type"], route["entity_id"])
        return api_response(
            data={"route": route, "actions": actions},
            message="Context actions",
        )


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


class ExplorerOverviewView(APIView):
    """Lightweight first paint — summary and preview only."""

    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        uid = _user_cache_id(request)
        org = _org_scope(request)
        with perf_span(f"explorer.overview:{entity_type}/{entity_id}"):
            data = cached_explorer(
                scope="overview",
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=uid,
                ttl=TTL_OVERVIEW,
                org_scope=org,
                builder=lambda: build_explorer_overview(request, entity_type, entity_id),
            )
            return api_response(data=data, message="Explorer overview")


class ExplorerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        uid = _user_cache_id(request)
        org = _org_scope(request)
        ttl = TTL_ENFORCEMENT if entity_type.startswith("enforcement") else TTL_NATIONAL_RISK
        bundle = cached_explorer(
            scope="detail",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=uid,
            ttl=ttl,
            org_scope=org,
            builder=lambda: build_explorer_bundle(request, entity_type, entity_id),
        )
        page, page_size = _page_params(request)
        if bundle.get("records"):
            bundle["records"] = paginate_list(bundle["records"], page=page, page_size=page_size)
        _audit_regulator_explore(user=request.user, entity_type=entity_type, entity_id=entity_id)
        return api_response(data=bundle, message="Explorer detail")


class ExplorerRelatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        uid = _user_cache_id(request)
        related = cached_explorer(
            scope="related",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=uid,
            ttl=TTL_NATIONAL_RISK,
            org_scope=_org_scope(request),
            builder=lambda: build_explorer_bundle(request, entity_type, entity_id).get("related_entities")
            or build_graph_stub(entity_type=entity_type, entity_id=entity_id, summary_row=None),
        )
        return api_response(data={"related_entities": related}, message="Related")


class ExplorerTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        page, page_size = _page_params(request)

        def _build():
            bundle = build_explorer_bundle(request, entity_type, entity_id)
            tl = bundle.get("timeline") or build_timeline_entries(entity_type, entity_id)
            return paginate_list(tl if isinstance(tl, list) else [], page=page, page_size=page_size)

        data = cached_explorer(
            scope=f"timeline:{page}:{page_size}",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=_user_cache_id(request),
            ttl=TTL_TIMELINE,
            org_scope=_org_scope(request),
            builder=_build,
        )
        return api_response(data={"timeline": data}, message="Timeline")


class ExplorerEvidenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, entity_type, entity_id):
        ok, reason = _check_explorer_access(request, entity_type, entity_id)
        if not ok:
            return api_response(message=reason, status_code=403 if reason != "not_found" else 404)
        page, page_size = _page_params(request)

        def _build():
            ev = build_evidence_entries(entity_type, entity_id)
            return paginate_list(ev if isinstance(ev, list) else [], page=page, page_size=page_size)

        data = cached_explorer(
            scope=f"evidence:{page}:{page_size}",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=_user_cache_id(request),
            ttl=TTL_TIMELINE,
            org_scope=_org_scope(request),
            builder=_build,
        )
        return api_response(data={"evidence": data}, message="Evidence")


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

        def _build():
            if is_aggregate_id(entity_id) and entity_id == "national-risk-current":
                return risk_breakdown.national_risk_breakdown()
            if entity_type == "regional_risk":
                return risk_breakdown.regional_risk_breakdown(entity_id)
            bundle = build_explorer_bundle(request, entity_type, entity_id)
            return bundle.get("risk_explanation") or {}

        data = cached_explorer(
            scope="risk",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=_user_cache_id(request),
            ttl=TTL_NATIONAL_RISK,
            org_scope=_org_scope(request),
            builder=_build,
        )
        return api_response(data=data, message="Risk breakdown")


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
        if result.get("ok"):
            on_enforcement_mutation(entity_type=entity_type, entity_id=entity_id)
        if not result.get("ok"):
            return api_response(data=result, message=result.get("error", "failed"), status_code=400)
        return api_response(data=result, message="Action executed", status_code=201)
