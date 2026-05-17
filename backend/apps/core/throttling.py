"""Rate limiting for national-scale API protection."""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class NPTTEAnonThrottle(AnonRateThrottle):
    scope = "anon"


class NPTTEUserThrottle(UserRateThrottle):
    scope = "user"


class AuthEndpointThrottle(AnonRateThrottle):
    """Stricter limits on authentication endpoints (brute-force protection)."""

    scope = "auth"


class VerificationPublicThrottle(AnonRateThrottle):
    scope = "verify"


class CitizenPublicThrottle(AnonRateThrottle):
    """Aggressive limits for public citizen verification and reporting."""

    scope = "citizen"


class CommandCenterThrottle(UserRateThrottle):
    """Regulator command center burst protection."""

    scope = "command"
