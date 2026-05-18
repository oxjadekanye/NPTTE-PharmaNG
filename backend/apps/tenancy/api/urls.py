from django.urls import path

from apps.tenancy.api import views

urlpatterns = [
    path("onboarding/apply/", views.OnboardingApplyView.as_view(), name="tenancy-onboarding-apply"),
    path("onboarding/<uuid:pk>/submit/", views.OnboardingSubmitView.as_view(), name="tenancy-onboarding-submit"),
    path("invitations/", views.InvitationListCreateView.as_view(), name="tenancy-invitations"),
    path("invitations/<uuid:pk>/resend/", views.InvitationResendView.as_view(), name="tenancy-invitation-resend"),
    path("invitations/<uuid:pk>/revoke/", views.InvitationRevokeView.as_view(), name="tenancy-invitation-revoke"),
    path("invitations/accept/", views.InvitationAcceptView.as_view(), name="tenancy-invitation-accept"),
    path("memberships/", views.MembershipListView.as_view(), name="tenancy-memberships"),
    path("context/current/", views.TenantContextView.as_view(), name="tenancy-context-current"),
    path("context/switch/", views.TenantContextSwitchView.as_view(), name="tenancy-context-switch"),
    path("dashboard/", views.OrganisationDashboardView.as_view(), name="tenancy-dashboard"),
    path("regulator/approval-queue/", views.RegulatorApprovalQueueView.as_view(), name="tenancy-approval-queue"),
    path("regulator/approve/<uuid:pk>/", views.RegulatorApproveView.as_view(), name="tenancy-regulator-approve"),
    path("regulator/reject/<uuid:pk>/", views.RegulatorRejectView.as_view(), name="tenancy-regulator-reject"),
    path("regulator/suspend/<uuid:org_id>/", views.RegulatorSuspendView.as_view(), name="tenancy-regulator-suspend"),
    path("regulator/reactivate/<uuid:org_id>/", views.RegulatorReactivateView.as_view(), name="tenancy-regulator-reactivate"),
]
