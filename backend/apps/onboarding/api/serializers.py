from rest_framework import serializers

from apps.onboarding.models import OrganisationOnboarding


class OnboardingSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(source="organisation.legal_name", read_only=True)

    class Meta:
        model = OrganisationOnboarding
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "reviewed_at")


class RejectSerializer(serializers.Serializer):
    reason = serializers.CharField()
