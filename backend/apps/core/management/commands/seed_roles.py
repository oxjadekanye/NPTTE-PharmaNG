"""Seed NPTTE platform roles."""
from django.core.management.base import BaseCommand

from apps.accounts.models import Role
from apps.core.constants import RoleCode


class Command(BaseCommand):
    help = "Create or update standard NPTTE platform roles."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for code, label in RoleCode.CHOICES:
            _, was_created = Role.objects.update_or_create(
                code=code,
                defaults={"name": label, "description": f"NPTTE role: {label}", "is_active": True},
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"Roles seeded: {created} created, {updated} updated.")
        )
