"""Account and authentication serializers."""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.core.roles import sync_regulator_flag
from apps.organisations.models import Organisation
from apps.patients.models import PatientProfile

User = get_user_model()

SELF_REGISTER_ROLES = RoleCode.SELF_REGISTER_CODES


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "code", "name", "description", "is_active")


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_code = serializers.CharField(source="role.code", read_only=True)
    organisation_name = serializers.CharField(
        source="organisation.legal_name",
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "national_id_number",
            "role",
            "role_code",
            "organisation",
            "organisation_name",
            "is_regulator",
            "status",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "is_regulator",
            "status",
            "date_joined",
            "role",
            "role_code",
            "organisation_name",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role_code = serializers.ChoiceField(
        choices=[(c, c) for c in sorted(SELF_REGISTER_ROLES)],
        default=RoleCode.PATIENT,
    )
    organisation_id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
            "national_id_number",
            "role_code",
            "organisation_id",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        role_code = attrs.get("role_code", RoleCode.PATIENT)
        if role_code not in SELF_REGISTER_ROLES:
            raise serializers.ValidationError(
                {"role_code": "This role cannot self-register. Contact an administrator."}
            )
        if role_code in RoleCode.PHARMACY_CODES and not attrs.get("organisation_id"):
            raise serializers.ValidationError(
                {"organisation_id": "Pharmacy staff must be linked to a pharmacy organisation."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        role_code = validated_data.pop("role_code")
        organisation_id = validated_data.pop("organisation_id", None)
        password = validated_data.pop("password")

        role = Role.objects.get(code=role_code)
        organisation = None
        if organisation_id:
            organisation = Organisation.objects.get(id=organisation_id)

        user = User(
            role=role,
            organisation=organisation,
            **validated_data,
        )
        user.set_password(password)
        sync_regulator_flag(user)
        user.save()

        if role_code == RoleCode.PATIENT:
            PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    "preferred_name": user.get_full_name() or user.username,
                    "phone_number": user.phone_number,
                },
            )

        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login payload with role and organisation context."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role_code"] = user.role_code or ""
        token["organisation_id"] = str(user.organisation_id) if user.organisation_id else ""
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class PermissionsSerializer(serializers.Serializer):
    role_code = serializers.CharField()
    is_regulator = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    organisation_id = serializers.UUIDField(allow_null=True)
    permissions = serializers.ListField(child=serializers.CharField())
