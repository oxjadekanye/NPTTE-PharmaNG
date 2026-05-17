from django.urls import path

from apps.onboarding.api.views import (
    OnboardingApproveView,
    OnboardingListView,
    OnboardingRejectView,
    OnboardingReviewView,
)

urlpatterns = [
    path("", OnboardingListView.as_view(), name="onboarding-list"),
    path("<uuid:pk>/approve/", OnboardingApproveView.as_view(), name="onboarding-approve"),
    path("<uuid:pk>/reject/", OnboardingRejectView.as_view(), name="onboarding-reject"),
    path("<uuid:pk>/review/", OnboardingReviewView.as_view(), name="onboarding-review"),
]
