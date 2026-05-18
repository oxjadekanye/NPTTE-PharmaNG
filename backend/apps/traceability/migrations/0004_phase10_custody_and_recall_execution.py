# Phase 10 — custody ledger and recall execution

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisations", "0001_initial"),
        ("serialization", "0004_phase10_serialization_operations"),
        ("traceability", "0003_rename_traceability_batch_created_idx_traceabilit_batch_i_1f2e0e_idx"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SerialCustodyEvent",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("source_node", models.CharField(blank=True, max_length=32)),
                ("destination_node", models.CharField(db_index=True, max_length=32)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("verification_signature", models.CharField(blank=True, max_length=256)),
                ("custody_confirmed", models.BooleanField(db_index=True, default=False)),
                ("integrity_status", models.CharField(db_index=True, default="pending", max_length=32)),
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
                    "destination_organisation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="custody_events_in",
                        to="organisations.organisation",
                    ),
                ),
                (
                    "product_serial",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custody_events",
                        to="serialization.productserial",
                    ),
                ),
                (
                    "source_organisation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="custody_events_out",
                        to="organisations.organisation",
                    ),
                ),
                (
                    "supply_chain_transaction",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="custody_events",
                        to="traceability.supplychaintransaction",
                    ),
                ),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="RecallExecutionCampaign",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("campaign_code", models.CharField(db_index=True, max_length=64, unique=True)),
                ("pharmacies_targeted", models.PositiveIntegerField(default=0)),
                ("pharmacies_acknowledged", models.PositiveIntegerField(default=0)),
                ("estimated_patient_exposure", models.PositiveIntegerField(default=0)),
                ("destruction_verified", models.BooleanField(default=False)),
                ("quarantine_active", models.BooleanField(db_index=True, default=True)),
                (
                    "batch_recall",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="execution_campaigns",
                        to="traceability.batchrecall",
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
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PharmacyRecallAcknowledgement",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("completion_pct", models.PositiveSmallIntegerField(default=0)),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pharmacy_acks",
                        to="traceability.recallexecutioncampaign",
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
                    "pharmacy_organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recall_acknowledgements",
                        to="organisations.organisation",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="serialcustodyevent",
            index=models.Index(fields=["product_serial", "created_at"], name="traceabilit_serial__p10_idx"),
        ),
    ]
