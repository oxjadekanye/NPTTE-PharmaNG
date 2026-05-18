# Phase 10 certificates

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0004_productbatch_lifecycle_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DigitalRegulatoryCertificate",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("certificate_number", models.CharField(db_index=True, max_length=64, unique=True)),
                ("certificate_type", models.CharField(db_index=True, max_length=64)),
                ("subject_label", models.CharField(max_length=255)),
                ("issued_at", models.DateTimeField(db_index=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("qr_verification_code", models.CharField(db_index=True, max_length=128, unique=True)),
                ("digital_signature", models.CharField(max_length=256)),
                ("tamper_hash", models.CharField(db_index=True, max_length=128)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="certificates",
                        to="products.productbatch",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "issued_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="issued_certificates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-issued_at"]},
        ),
    ]
