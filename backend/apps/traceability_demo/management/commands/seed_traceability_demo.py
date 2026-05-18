from django.core.management.base import BaseCommand

from apps.traceability_demo.seed import seed_traceability_demo


class Command(BaseCommand):
    help = "Seed national traceability end-to-end demo data (tagged traceability_demo)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-seed even if demo data already exists (prefer clear_traceability_demo first).",
        )

    def handle(self, *args, **options):
        result = seed_traceability_demo(force=options["force"])
        self.stdout.write(self.style.SUCCESS(str(result)))
