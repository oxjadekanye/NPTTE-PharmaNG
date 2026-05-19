"""Pre-warm hot explorer context caches after demo seed."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.explorer.services.cache import cached_explorer
from apps.explorer.services.context_router import resolve_context_route
from apps.explorer.services.quick_explorer import build_quick_bundle
from apps.explorer.services.overview import build_explorer_overview

HOT_CONTEXTS = [
    "national_status",
    "national_risk",
    "verifications_24h",
    "counterfeit_detections",
    "open_alerts",
    "fraud_flags",
    "active_investigations",
    "emergency_recalls",
    "blacklisted_batches",
    "live_national_threat_composite",
    "api_health",
    "medicine_stability",
    "counterfeit_risk_forecast",
    "shortage_pressure",
    "enforcement_readiness",
    "urgent_actions",
]


class Command(BaseCommand):
    help = "Warm Redis/Django cache for hot dashboard explorer contexts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default="",
            help="Regulator user to warm cache as (defaults to first regulator/superuser).",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        user = None
        if options.get("username"):
            user = User.objects.filter(username=options["username"]).first()
        if user is None:
            user = User.objects.filter(is_regulator=True).first() or User.objects.filter(is_superuser=True).first()
        if user is None:
            self.stderr.write("No regulator user found — create one or pass --username")
            return

        uid = str(user.pk)
        warmed = 0
        for ctx in HOT_CONTEXTS:
            route = resolve_context_route(context_key=ctx, user=user)
            et, eid = route["entity_type"], route["entity_id"]
            cached_explorer(
                scope="quick-bundle:1:25",
                entity_type="context",
                entity_id=ctx,
                user_id=uid,
                ttl=120,
                builder=lambda c=ctx: build_quick_bundle(context_key=c, request=None, page=1, page_size=25),
            )
            cached_explorer(
                scope="overview",
                entity_type=et,
                entity_id=eid,
                user_id=uid,
                ttl=90,
                builder=lambda t=et, i=eid: build_explorer_overview(None, t, i),
            )
            warmed += 1
            self.stdout.write(f"  warmed {ctx} -> {et}/{eid}")

        self.stdout.write(self.style.SUCCESS(f"Warmed {warmed} hot contexts for user {user.username}"))
