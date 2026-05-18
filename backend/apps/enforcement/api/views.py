"""Phase 18 — enforcement APIs."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.enforcement.models import EnforcementCase, EnforcementRecommendation, EnforcementTimelineEntry
from apps.enforcement.services.cases import assign_case, create_enforcement_case
from apps.enforcement.services.recommendations import accept_recommendation, create_recommendation, dismiss_recommendation
from apps.organisations.models import Organisation
from apps.tenancy.services.tenant import get_active_organisation_id, user_can_access_organisation


def _filter_cases(request):
    qs = EnforcementCase.objects.select_related("organisation", "assigned_regulator").order_by("-created_at")
    if not is_regulator_user(request.user) and not request.user.is_superuser:
        org_id = get_active_organisation_id(request)
        qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
    return qs


class EnforcementCaseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = [
            {
                "id": str(c.id),
                "case_reference": c.case_reference,
                "title": c.title,
                "case_status": c.case_status,
                "severity": c.severity,
                "organisation_id": str(c.organisation_id) if c.organisation_id else None,
            }
            for c in _filter_cases(request)[:50]
        ]
        return api_response(data={"cases": rows}, message="Enforcement cases")

    def post(self, request):
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            return api_response(message="Regulator access required", status_code=403)
        org = None
        org_id = request.data.get("organisation_id")
        if org_id:
            org = Organisation.objects.filter(pk=org_id).first()
        case = create_enforcement_case(
            title=request.data["title"],
            summary=request.data.get("summary", ""),
            severity=request.data.get("severity", EnforcementCase.SEV_MEDIUM),
            organisation=org,
            actor=request.user,
        )
        return api_response(data={"id": str(case.id), "reference": case.case_reference}, message="Case created", status_code=201)


class EnforcementCaseAssignView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        case = EnforcementCase.objects.get(pk=pk)
        investigator = User.objects.get(pk=request.data["investigator_id"])
        assign_case(case=case, investigator=investigator, actor=request.user, notes=request.data.get("notes", ""))
        return api_response(data={"id": str(case.id)}, message="Case assigned")


class EnforcementRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = EnforcementRecommendation.objects.filter(
            recommendation_status=EnforcementRecommendation.STATUS_PENDING
        ).order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = get_active_organisation_id(request)
            qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
        rows = [
            {
                "id": str(r.id),
                "recommendation_type": r.recommendation_type,
                "title": r.title,
                "severity": r.severity,
                "risk_score": float(r.risk_score),
                "organisation_id": str(r.organisation_id) if r.organisation_id else None,
            }
            for r in qs[:50]
        ]
        return api_response(data={"recommendations": rows}, message="Enforcement recommendations")


class RecommendationAcceptView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        rec = EnforcementRecommendation.objects.get(pk=pk)
        accept_recommendation(recommendation=rec, actor=request.user)
        return api_response(data={"id": str(rec.id)}, message="Recommendation accepted")


class RecommendationDismissView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        rec = EnforcementRecommendation.objects.get(pk=pk)
        dismiss_recommendation(recommendation=rec, actor=request.user)
        return api_response(data={"id": str(rec.id)}, message="Recommendation dismissed")


class EnforcementTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        case_id = request.query_params.get("case_id")
        qs = EnforcementTimelineEntry.objects.select_related("case").order_by("-created_at")
        if case_id:
            qs = qs.filter(case_id=case_id)
            case = EnforcementCase.objects.get(pk=case_id)
            if case.organisation_id and not user_can_access_organisation(request.user, case.organisation_id):
                if not is_regulator_user(request.user):
                    return api_response(message="Access denied", status_code=403)
        elif not is_regulator_user(request.user):
            org_id = get_active_organisation_id(request)
            qs = qs.filter(case__organisation_id=org_id) if org_id else qs.none()
        rows = [
            {
                "id": str(e.id),
                "entry_type": e.entry_type,
                "summary": e.summary,
                "case_id": str(e.case_id) if e.case_id else None,
                "created_at": e.created_at.isoformat(),
            }
            for e in qs[:100]
        ]
        return api_response(data={"timeline": rows}, message="Enforcement timeline")
