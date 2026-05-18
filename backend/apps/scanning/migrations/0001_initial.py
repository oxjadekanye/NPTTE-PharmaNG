# Phase 12 — ScanEvent

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organisations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ScanEvent",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("serial_number", models.CharField(db_index=True, max_length=128)),
                ("scan_type", models.CharField(db_index=True, max_length=64)),
                ("actor_role", models.CharField(blank=True, db_index=True, max_length=64)),
                ("device_id", models.CharField(blank=True, db_index=True, max_length=128)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("offline_timestamp", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("sync_status", models.CharField(db_index=True, default="synced", max_length=32)),
                ("risk_score", models.DecimalField(db_index=True, decimal_places=2, default=0, max_digits=5)),
                ("outcome_label", models.CharField(blank=True, db_index=True, max_length=64)),
                ("result_payload", models.JSONField(blank=True, default=dict)),
                ("replay_nonce", models.CharField(blank=True, db_index=True, max_length=64)),
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
                    "organisation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="scan_events",
                        to="organisations.organisation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="scan_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="scanevent",
            index=models.Index(fields=["serial_number", "created_at"], name="scanning_se_serial_created_idx"),
        ),
        migrations.AddIndex(
            model_name="scanevent",
            index=models.Index(fields=["scan_type", "sync_status"], name="scanning_se_type_sync_idx"),
        ),
    ]
