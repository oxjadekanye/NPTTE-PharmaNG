from django.db import connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.permissions import IsRegulatorUser
from apps.pilot_readiness.api_catalog import build_api_readiness
from apps.pilot_readiness.demo_control import clear_demo_data, demo_inventory, seed_demo_incident, seed_demo_products
from apps.pilot_readiness.performance import build_performance_readiness
from apps.pilot_readiness.readiness import build_readiness_report
from apps.pilot_readiness.security_status import build_security_status
from apps.pilot_readiness.workflows import onboarding_workflow_board


class PilotReadinessView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=build_readiness_report(), message="Pilot readiness report")


class OnboardingWorkflowsView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data={"workflows": onboarding_workflow_board()}, message="Onboarding workflows")


class DemoControlView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=demo_inventory(), message="Demo data inventory")

    def post(self, request):
        action = request.data.get("action")
        if action == "seed_products":
            data = seed_demo_products(actor=request.user)
        elif action == "seed_incident":
            data = seed_demo_incident(actor=request.user)
        elif action == "clear_demo":
            data = clear_demo_data()
        else:
            return api_response(data={}, message="Unknown action", status_code=400)
        return api_response(data=data, message=f"Demo action: {action}")


class ApiReadinessView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        return api_response(data=build_api_readiness(health_ok=db_ok), message="API readiness")


class SecurityReadinessView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=build_security_status(), message="Security posture")


class PerformanceReadinessView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get(self, request):
        return api_response(data=build_performance_readiness(), message="Performance readiness")
