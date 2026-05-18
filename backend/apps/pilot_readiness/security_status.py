"""Non-secret security posture summary for pilot dashboards."""
from __future__ import annotations

from django.conf import settings


def build_security_status() -> dict:
    cors_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", []) or []
    jwt_configured = "rest_framework_simplejwt.authentication.JWTAuthentication" in (
        settings.REST_FRAMEWORK.get("DEFAULT_AUTHENTICATION_CLASSES", [])
    )
    default_auth = settings.REST_FRAMEWORK.get("DEFAULT_PERMISSION_CLASSES", [])
    rbac_enforced = "rest_framework.permissions.IsAuthenticated" in str(default_auth)
    audit_middleware = "apps.core.middleware.APIAuditMiddleware" in settings.MIDDLEWARE

    return {
        "jwt_status": "active" if jwt_configured else "review_required",
        "cors_status": "configured" if cors_origins else "permissive_or_env_pending",
        "cors_origin_count": len(cors_origins),
        "rbac_status": "enforced_via_drf_permissions" if rbac_enforced else "review",
        "audit_logging_status": "active" if audit_middleware else "inactive",
        "suspicious_access_monitoring": "demo_ui_stub",
        "failed_login_monitoring": "demo_ui_stub",
        "regulator_access_overview": "role_gated_nafdac_and_regulator_codes",
        "secrets_exposed": False,
        "note": "No secrets returned — verify Render/Vercel env in deployment console.",
    }
