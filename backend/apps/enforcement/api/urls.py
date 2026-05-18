from django.urls import path

from apps.enforcement.api.views import (
    EnforcementCaseAssignView,
    EnforcementCaseListView,
    EnforcementRecommendationsView,
    EnforcementTimelineView,
    RecommendationAcceptView,
    RecommendationDismissView,
)

urlpatterns = [
    path("cases/", EnforcementCaseListView.as_view(), name="enforcement-cases"),
    path("cases/<uuid:pk>/assign/", EnforcementCaseAssignView.as_view(), name="enforcement-case-assign"),
    path("recommendations/", EnforcementRecommendationsView.as_view(), name="enforcement-recommendations"),
    path("recommendations/<uuid:pk>/accept/", RecommendationAcceptView.as_view(), name="enforcement-rec-accept"),
    path("recommendations/<uuid:pk>/dismiss/", RecommendationDismissView.as_view(), name="enforcement-rec-dismiss"),
    path("timeline/", EnforcementTimelineView.as_view(), name="enforcement-timeline"),
]
