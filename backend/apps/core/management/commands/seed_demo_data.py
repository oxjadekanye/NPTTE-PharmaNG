"""
Seed safe demonstration data for local and staging validation.

Does not overwrite existing production records unless --force is passed.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management import call_command

from apps.accounts.models import Role
from apps.core.constants import AvailabilityStatus, RoleCode
from apps.inventory.models import InventoryItem
from apps.organisations.models import Organisation, OrganisationType
from apps.patients.models import PatientProfile
from apps.pharmacies.models import PharmacyProfile
from apps.products.models import Product

User = get_user_model()

DEMO_PHARMACIES = [
    {
        "legal_name": "Lagos Central Pharmacy Ltd",
        "trading_name": "Lagos Central Pharmacy",
        "city": "Lagos",
        "state": "Lagos",
        "lat": Decimal("6.5244"),
        "lon": Decimal("3.3792"),
        "license": "PH-LG-001",
    },
    {
        "legal_name": "Abuja MediCare Pharmacy",
        "trading_name": "Abuja MediCare",
        "city": "Abuja",
        "state": "FCT",
        "lat": Decimal("9.0765"),
        "lon": Decimal("7.3986"),
        "license": "PH-AB-002",
    },
    {
        "legal_name": "Port Harcourt Health Pharmacy",
        "trading_name": "PH Health Pharmacy",
        "city": "Port Harcourt",
        "state": "Rivers",
        "lat": Decimal("4.8156"),
        "lon": Decimal("7.0498"),
        "license": "PH-PH-003",
    },
]

DEMO_PRODUCTS = [
    {
        "name": "Paracetamol",
        "brand_name": "Panadol",
        "active_ingredient": "Paracetamol",
        "strength": "500mg",
        "dosage_form": "Tablet",
    },
    {
        "name": "Amoxicillin",
        "brand_name": "Amoxil",
        "active_ingredient": "Amoxicillin",
        "strength": "500mg",
        "dosage_form": "Capsule",
    },
    {
        "name": "Metformin",
        "brand_name": "Glucophage",
        "active_ingredient": "Metformin",
        "strength": "500mg",
        "dosage_form": "Tablet",
    },
]


class Command(BaseCommand):
    help = "Seed demo pharmacies, products, inventory, and a patient user."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recreate demo inventory quantities.",
        )

    def handle(self, *args, **options):
        call_command("seed_roles")

        pharmacy_type, _ = OrganisationType.objects.get_or_create(
            code="pharmacy",
            defaults={"name": "Pharmacy", "description": "Licensed retail pharmacy"},
        )

        organisations = []
        for item in DEMO_PHARMACIES:
            org, _ = Organisation.objects.get_or_create(
                legal_name=item["legal_name"],
                defaults={
                    "organisation_type": pharmacy_type,
                    "trading_name": item["trading_name"],
                    "city": item["city"],
                    "state": item["state"],
                    "country": "NG",
                    "latitude": item["lat"],
                    "longitude": item["lon"],
                    "phone_number": "+2348000000001",
                    "address_line_1": f"1 Demo Street, {item['city']}",
                },
            )
            PharmacyProfile.objects.get_or_create(
                organisation=org,
                defaults={
                    "pharmacy_license_number": item["license"],
                    "opening_hours": {
                        "monday": {"open": "08:00", "close": "20:00"},
                        "tuesday": {"open": "08:00", "close": "20:00"},
                        "wednesday": {"open": "08:00", "close": "20:00"},
                        "thursday": {"open": "08:00", "close": "20:00"},
                        "friday": {"open": "08:00", "close": "20:00"},
                        "saturday": {"open": "09:00", "close": "18:00"},
                        "sunday": {"closed": True},
                    },
                },
            )
            organisations.append(org)

        products = []
        for pdata in DEMO_PRODUCTS:
            product, _ = Product.objects.get_or_create(
                name=pdata["name"],
                strength=pdata["strength"],
                dosage_form=pdata["dosage_form"],
                defaults={
                    "brand_name": pdata["brand_name"],
                    "active_ingredient": pdata["active_ingredient"],
                },
            )
            products.append(product)

        for org in organisations:
            for product in products:
                qty = 50 if options["force"] else 25
                InventoryItem.objects.update_or_create(
                    organisation=org,
                    product=product,
                    batch=None,
                    defaults={
                        "quantity_on_hand": qty,
                        "availability_status": AvailabilityStatus.IN_STOCK,
                        "is_active": True,
                    },
                )

        patient_role = Role.objects.get(code=RoleCode.PATIENT)
        patient_user, created = User.objects.get_or_create(
            username="demo_patient",
            defaults={
                "email": "patient@demo.nptte.gov.ng",
                "role": patient_role,
                "first_name": "Demo",
                "last_name": "Patient",
            },
        )
        if created:
            patient_user.set_password("DemoPatient2026!")
            patient_user.save()

        PatientProfile.objects.get_or_create(
            user=patient_user,
            defaults={
                "preferred_name": "Demo Patient",
                "consent_to_location_search": True,
            },
        )

        pharmacy_role = Role.objects.get(code=RoleCode.PHARMACY_ADMIN)
        if organisations:
            pharm_user, pc = User.objects.get_or_create(
                username="demo_pharmacy_admin",
                defaults={
                    "email": "pharmacy@demo.nptte.gov.ng",
                    "role": pharmacy_role,
                    "organisation": organisations[0],
                },
            )
            if pc:
                pharm_user.set_password("DemoPharmacy2026!")
                pharm_user.save()

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("  demo_patient / DemoPatient2026!")
        self.stdout.write("  demo_pharmacy_admin / DemoPharmacy2026!")
