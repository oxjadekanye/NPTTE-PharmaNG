from django.urls import path

from apps.pilot_readiness.api.views import (
    ApiReadinessView,
    DemoControlView,
    OnboardingWorkflowsView,
    PerformanceReadinessView,
    PilotReadinessView,
    SecurityReadinessView,
)

urlpatterns = [
    path("readiness/", PilotReadinessView.as_view(), name="pilot-readiness"),
    path("onboarding-workflows/", OnboardingWorkflowsView.as_view(), name="pilot-onboarding-workflows"),
    path("demo-control/", DemoControlView.as_view(), name="pilot-demo-control"),
    path("api-readiness/", ApiReadinessView.as_view(), name="pilot-api-readiness"),
    path("security/", SecurityReadinessView.as_view(), name="pilot-security"),
    path("performance/", PerformanceReadinessView.as_view(), name="pilot-performance"),
]
