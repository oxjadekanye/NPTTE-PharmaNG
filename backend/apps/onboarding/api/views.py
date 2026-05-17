from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.responses import api_response
from apps.core.constants import OnboardingStatus
from apps.core.permissions import IsRegulatorUser
from apps.onboarding.api.serializers import OnboardingSerializer, RejectSerializer
from apps.onboarding.models import OrganisationOnboarding
from apps.onboarding.services import approve_organisation, reject_organisation, request_compliance_review


class OnboardingListView(generics.ListAPIView):
    serializer_class = OnboardingSerializer
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def get_queryset(self):
        qs = OrganisationOnboarding.objects.select_related("organisation", "organisation_type")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            return qs.filter(status=status_filter)
        return qs.filter(status=OnboardingStatus.UNDER_REVIEW)


class OnboardingApproveView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        onboarding = OrganisationOnboarding.objects.get(pk=pk)
        approve_organisation(onboarding=onboarding, actor=request.user, request=request)
        return api_response(data=OnboardingSerializer(onboarding).data, message="Organisation approved")


class OnboardingRejectView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        ser = RejectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        onboarding = OrganisationOnboarding.objects.get(pk=pk)
        reject_organisation(
            onboarding=onboarding, actor=request.user, reason=ser.validated_data["reason"], request=request
        )
        return api_response(data=OnboardingSerializer(onboarding).data, message="Organisation rejected")


class OnboardingReviewView(APIView):
    permission_classes = [IsAuthenticated, IsRegulatorUser]

    def post(self, request, pk):
        onboarding = OrganisationOnboarding.objects.get(pk=pk)
        request_compliance_review(onboarding=onboarding, actor=request.user, request=request)
        return api_response(data=OnboardingSerializer(onboarding).data, message="Compliance review requested")
