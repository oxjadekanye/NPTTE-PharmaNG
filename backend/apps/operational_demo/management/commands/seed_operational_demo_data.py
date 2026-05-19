from django.core.management.base import BaseCommand

from apps.operational_demo.seed import is_seeded, seed_operational_demo_data


class Command(BaseCommand):
    help = "Seed national-scale operational demo data (idempotent). Tags metadata.demo_type=national_operational_demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-run seed even if demo data already exists (additive; may duplicate some keyed records).",
        )
        parser.add_argument(
            "--lite",
            action="store_true",
            help="Smaller dataset for CI/local quick runs.",
        )

    def handle(self, *args, **options):
        if is_seeded() and not options["force"]:
            self.stdout.write(self.style.WARNING("Operational demo already seeded. Use --force to add more."))
            return
        result = seed_operational_demo_data(lite=options["lite"], force=options["force"])
        self.stdout.write(self.style.SUCCESS(str(result)))
