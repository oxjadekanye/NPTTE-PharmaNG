from django.core.management.base import BaseCommand

from apps.traceability_demo.clear import clear_traceability_demo


class Command(BaseCommand):
    help = "Delete only records tagged metadata.demo_type=traceability_demo."

    def handle(self, *args, **options):
        result = clear_traceability_demo()
        self.stdout.write(self.style.SUCCESS(str(result)))
