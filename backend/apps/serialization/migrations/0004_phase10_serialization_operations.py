# Generated manually for Phase 10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_productbatch_lifecycle_status"),
        ("serialization", "0003_productserial_custody_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="productserial",
            name="counterfeit_probability",
            field=models.DecimalField(
                db_index=True,
                decimal_places=2,
                default=0,
                help_text="Last computed counterfeit probability (0–100).",
                max_digits=5,
            ),
        ),
        migrations.AddField(
            model_name="productserial",
            name="gs1_element_string",
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AddField(
            model_name="productserial",
            name="gtin14",
            field=models.CharField(blank=True, db_index=True, max_length=14),
        ),
        migrations.CreateModel(
            name="SerialPackagingUnit",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("pack_code", models.CharField(db_index=True, max_length=128, unique=True)),
                ("level", models.CharField(db_index=True, max_length=32)),
                ("serial_count", models.PositiveIntegerField(default=0)),
                ("sscc", models.CharField(blank=True, db_index=True, help_text="GS1 SSCC when applicable.", max_length=20)),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="packaging_units",
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
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="serialization.serialpackagingunit",
                    ),
                ),
            ],
            options={
                "verbose_name": "Serial packaging unit",
                "verbose_name_plural": "Serial packaging units",
                "ordering": ["pack_code"],
            },
        ),
        migrations.AddField(
            model_name="productserial",
            name="packaging_unit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="serials",
                to="serialization.serialpackagingunit",
            ),
        ),
        migrations.CreateModel(
            name="SerialScanRecord",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("serial_number", models.CharField(db_index=True, max_length=128)),
                ("scan_source", models.CharField(db_index=True, help_text="citizen, pharmacy, warehouse, customs, regulator", max_length=32)),
                ("scanner_type", models.CharField(blank=True, db_index=True, max_length=32)),
                ("outcome", models.CharField(blank=True, db_index=True, max_length=64)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("device_fingerprint", models.CharField(blank=True, db_index=True, max_length=64)),
                ("replay_nonce", models.CharField(blank=True, db_index=True, max_length=64)),
                ("is_duplicate", models.BooleanField(db_index=True, default=False)),
                ("is_suspicious", models.BooleanField(db_index=True, default=False)),
                ("scan_metadata", models.JSONField(blank=True, default=dict)),
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
                    "product_serial",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scan_records",
                        to="serialization.productserial",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="serialscanrecord",
            index=models.Index(fields=["serial_number", "created_at"], name="serializat_serial__a1b2c3_idx"),
        ),
        migrations.AddIndex(
            model_name="serialscanrecord",
            index=models.Index(fields=["replay_nonce"], name="serializat_replay__d4e5f6_idx"),
        ),
    ]
