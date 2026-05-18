"""API readiness catalog for pilot integrations (Phase 11)."""
from __future__ import annotations

API_GROUPS = [
    {"group": "health", "prefix": "/api/v1/health/", "auth": "none", "roles": []},
    {"group": "auth", "prefix": "/api/v1/auth/", "auth": "jwt", "roles": ["all_authenticated"]},
    {"group": "traceability", "prefix": "/api/v1/traceability/", "auth": "jwt", "roles": ["organisation_member", "regulator"]},
    {"group": "verification", "prefix": "/api/v1/verification/", "auth": "mixed", "roles": ["public_authenticate", "regulator_history"]},
    {"group": "public", "prefix": "/api/v1/public/", "auth": "none", "roles": ["citizen"]},
    {"group": "regulatory", "prefix": "/api/v1/regulatory/", "auth": "jwt", "roles": ["regulator"]},
    {"group": "command-center", "prefix": "/api/v1/command-center/", "auth": "jwt", "roles": ["regulator"]},
    {"group": "serialization", "prefix": "/api/v1/serialization/", "auth": "jwt", "roles": ["regulator"]},
    {"group": "intelligence", "prefix": "/api/v1/intelligence/", "auth": "jwt", "roles": ["regulator"]},
    {"group": "onboarding", "prefix": "/api/v1/onboarding/", "auth": "jwt", "roles": ["regulator"]},
    {"group": "pilot", "prefix": "/api/v1/pilot/", "auth": "jwt", "roles": ["regulator"]},
    {"group": "realtime", "prefix": "/api/v1/realtime/stream/", "auth": "none", "roles": ["sse_clients"]},
    {"group": "mobile", "prefix": "/api/v1/mobile/", "auth": "jwt", "roles": ["field_operators"]},
    {"group": "developer", "prefix": "/api/v1/developer/", "auth": "jwt", "roles": ["regulator"]},
]


def build_api_readiness(*, health_ok: bool = True) -> dict:
    groups = []
    for g in API_GROUPS:
        groups.append(
            {
                **g,
                "endpoint_health": "ok" if health_ok or g["group"] == "health" else "check_deploy",
                "last_successful_response": "at_deploy" if health_ok else "unknown",
                "warnings": [] if g["group"] != "realtime" else ["SSE requires long-lived connection — configure proxy timeout"],
            }
        )
    missing = [w for g in groups for w in g.get("warnings", [])]
    return {"groups": groups, "missing_integration_warnings": missing}
