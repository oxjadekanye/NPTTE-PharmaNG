"""Phase 18 — sovereign intelligence APIs."""
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.core.roles import is_regulator_user
from apps.intelligence.models import CounterfeitCluster, IntelligenceNarrative, IntelligenceSignal
from apps.intelligence.services.correlation import run_correlation
from apps.intelligence.services.narratives import generate_executive_briefing, generate_narrative
from apps.intelligence.services.national import (
    refresh_national_snapshot,
    refresh_organisation_profile,
    refresh_product_profile,
    refresh_regional_profile,
)
from apps.intelligence.services.scoring import (
    calculate_national_risk,
    calculate_organisation_risk,
    calculate_product_risk,
    calculate_regional_risk,
)
from apps.enforcement.services.automation import process_risk_threshold
from apps.organisations.models import Organisation
from apps.products.models import Product
from apps.tenancy.services.tenant import get_active_organisation_id, user_can_access_organisation


class NationalRiskView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        risk = calculate_national_risk()
        snap = refresh_national_snapshot()
        process_risk_threshold(risk_result=risk, context="national")
        return api_response(
            data={**risk, "snapshot_id": str(snap.id)},
            message="National risk intelligence",
        )


class RegionalRiskView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        state = request.query_params.get("state", "")
        if not state:
            states = Organisation.objects.exclude(state="").values_list("state", flat=True).distinct()[:12]
            rows = []
            for s in states:
                risk = calculate_regional_risk(region_state=s)
                rows.append({"region_state": s, **risk})
            return api_response(data={"regions": rows}, message="Regional risk intelligence")
        risk = calculate_regional_risk(region_state=state)
        profile = refresh_regional_profile(state)
        return api_response(data={**risk, "profile_id": str(profile.id), "region_state": state}, message="Regional risk")


class ProductRiskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            return api_response(message="Regulator access required", status_code=403)
        product_id = request.query_params.get("product_id")
        if product_id:
            product = Product.objects.get(pk=product_id)
            risk = calculate_product_risk(product=product)
            profile = refresh_product_profile(product)
            return api_response(data={**risk, "product_id": str(product.id)}, message="Product risk")
        products = Product.objects.all()[:25]
        rows = []
        for p in products:
            risk = calculate_product_risk(product=p)
            rows.append({"product_id": str(p.id), "name": p.name, **risk})
        return api_response(data={"products": rows}, message="Product risk table")


class OrganisationRiskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_id = request.query_params.get("organisation_id") or get_active_organisation_id(request)
        if not org_id:
            return api_response(message="organisation_id required", status_code=400)
        if not user_can_access_organisation(request.user, org_id):
            return api_response(message="Access denied", status_code=403)
        org = Organisation.objects.get(pk=org_id)
        risk = calculate_organisation_risk(organisation=org)
        profile = refresh_organisation_profile(org)
        if is_regulator_user(request.user):
            process_risk_threshold(risk_result=risk, organisation=org, context="organisation")
        return api_response(
            data={**risk, "organisation_id": str(org.id), "integrity_score": float(profile.integrity_score)},
            message="Organisation risk profile",
        )


class IntelligenceSignalsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = IntelligenceSignal.objects.filter(is_active=True).order_by("-created_at")
        if not is_regulator_user(request.user) and not request.user.is_superuser:
            org_id = get_active_organisation_id(request)
            qs = qs.filter(organisation_id=org_id) if org_id else qs.none()
        rows = [
            {
                "id": str(s.id),
                "signal_type": s.signal_type,
                "severity": s.severity,
                "title": s.title,
                "summary": s.summary,
                "confidence": float(s.confidence),
                "organisation_id": str(s.organisation_id) if s.organisation_id else None,
            }
            for s in qs[:50]
        ]
        return api_response(data={"signals": rows}, message="Intelligence signals")


class CounterfeitClustersView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        clusters = CounterfeitCluster.objects.filter(status="open").order_by("-suspicious_count")[:30]
        rows = [
            {
                "cluster_code": c.cluster_code,
                "scan_count": c.scan_count,
                "suspicious_count": c.suspicious_count,
                "confidence": float(c.confidence),
                "region_state": c.region_state,
                "product_id": str(c.product_id) if c.product_id else None,
            }
            for c in clusters
        ]
        return api_response(data={"clusters": rows}, message="Counterfeit clusters")


class RunCorrelationView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request):
        result = run_correlation(
            window_hours=int(request.data.get("window_hours", 24)),
            suspicious_threshold=int(request.data.get("threshold", 3)),
        )
        return api_response(data=result, message="Correlation complete", status_code=201)


class NarrativesView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        ntype = request.query_params.get("type")
        qs = IntelligenceNarrative.objects.order_by("-created_at")
        if ntype:
            qs = qs.filter(narrative_type=ntype)
        rows = [
            {"id": str(n.id), "narrative_type": n.narrative_type, "title": n.title, "body": n.body}
            for n in qs[:20]
        ]
        return api_response(data={"narratives": rows}, message="Intelligence narratives")

    def post(self, request):
        if request.data.get("executive_briefing"):
            data = generate_executive_briefing()
            return api_response(data=data, message="Executive briefing generated", status_code=201)
        narrative = generate_narrative(
            narrative_type=request.data.get("narrative_type", IntelligenceNarrative.NARRATIVE_EXECUTIVE),
            context=request.data.get("context", {}),
        )
        return api_response(
            data={"id": str(narrative.id), "title": narrative.title, "body": narrative.body},
            message="Narrative generated",
            status_code=201,
        )


class ExecutiveBriefingView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=generate_executive_briefing(), message="Executive briefing")


class NationalOperationsMetricsView(APIView):
    """Phase 11 — executive national operational readiness metrics."""

    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        from apps.intelligence.services.national_operations import build_national_operations_metrics

        return api_response(
            data=build_national_operations_metrics(),
            message="National operations metrics",
        )
