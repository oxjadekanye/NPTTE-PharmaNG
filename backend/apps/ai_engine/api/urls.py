from django.urls import path

from apps.ai_engine.api.views import NationalIntelligenceView, SerialRiskScoreView

urlpatterns = [
    path("national/", NationalIntelligenceView.as_view(), name="intelligence-national"),
    path("serial-risk/", SerialRiskScoreView.as_view(), name="intelligence-serial-risk"),
]
