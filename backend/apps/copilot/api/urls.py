from django.urls import path

from apps.copilot.api.views import (
    CopilotDraftEnforcementNoteView,
    CopilotExecutiveBriefingView,
    CopilotExplainRiskView,
    CopilotGenerateBriefingView,
    CopilotRecommendActionsView,
    CopilotSummariseInvestigationView,
)

urlpatterns = [
    path("explain-risk/", CopilotExplainRiskView.as_view(), name="copilot-explain-risk"),
    path("generate-briefing/", CopilotGenerateBriefingView.as_view(), name="copilot-generate-briefing"),
    path("recommend-actions/", CopilotRecommendActionsView.as_view(), name="copilot-recommend-actions"),
    path(
        "summarise-investigation/",
        CopilotSummariseInvestigationView.as_view(),
        name="copilot-summarise-investigation",
    ),
    path(
        "draft-enforcement-note/",
        CopilotDraftEnforcementNoteView.as_view(),
        name="copilot-draft-enforcement-note",
    ),
    path("executive-briefing/", CopilotExecutiveBriefingView.as_view(), name="copilot-executive-briefing"),
]
