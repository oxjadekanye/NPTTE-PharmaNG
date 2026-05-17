"""
Seed a national regulator / superuser account for command-center and admin access.

Safe to run multiple times (get_or_create). Override credentials via environment variables
on production — never rely on defaults outside local/staging.
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Role
from apps.core.constants import RoleCode
from apps.core.roles import sync_regulator_flag

User = get_user_model()

DEFAULT_USERNAME = "nptte_admin"
DEFAULT_EMAIL = "admin@nptte.gov.ng"
DEFAULT_ROLE = RoleCode.NAFDAC_ADMIN


class Command(BaseCommand):
    help = "Create or update the national regulator admin user (JWT + command center)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=os.environ.get("NPTTE_REGULATOR_USERNAME", DEFAULT_USERNAME),
        )
        parser.add_argument(
            "--email",
            default=os.environ.get("NPTTE_REGULATOR_EMAIL", DEFAULT_EMAIL),
        )
        parser.add_argument(
            "--role",
            default=os.environ.get("NPTTE_REGULATOR_ROLE", DEFAULT_ROLE),
            help="Role code (e.g. NAFDAC_ADMIN, SUPER_ADMIN)",
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Update password even if user already exists",
        )

    def handle(self, *args, **options):
        call_command("seed_roles")

        password = os.environ.get("NPTTE_REGULATOR_PASSWORD")
        if not password:
            if settings.DEBUG:
                password = "NptteAdmin2026!"
                self.stdout.write(
                    self.style.WARNING(
                        "Using default DEBUG password. Set NPTTE_REGULATOR_PASSWORD in production."
                    )
                )
            else:
                raise CommandError(
                    "Set NPTTE_REGULATOR_PASSWORD before running this command in production."
                )

        role_code = options["role"]
        try:
            role = Role.objects.get(code=role_code)
        except Role.DoesNotExist:
            raise CommandError(f"Role {role_code} not found. Run seed_roles first.")

        username = options["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": options["email"],
                "role": role,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if not created:
            user.email = options["email"]
            user.role = role
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True

        if created or options["reset_password"]:
            user.set_password(password)
        sync_regulator_flag(user)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} regulator admin: {username}"))
        self.stdout.write(f"  Role: {role_code}")
        self.stdout.write(f"  Email: {user.email}")
        self.stdout.write("  Use these credentials at /login on the Vercel frontend.")
        if settings.DEBUG and not os.environ.get("NPTTE_REGULATOR_PASSWORD"):
            self.stdout.write(f"  Password (DEBUG default): {password}")
