# Phase 10 offline scan queue

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mobile", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OfflineScanQueue",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("raw_scan", models.CharField(max_length=512)),
                ("scan_source", models.CharField(db_index=True, max_length=32)),
                ("scanner_type", models.CharField(blank=True, max_length=32)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("replay_nonce", models.CharField(blank=True, db_index=True, max_length=64)),
                ("sync_status", models.CharField(db_index=True, default="pending", max_length=32)),
                ("sync_attempts", models.PositiveSmallIntegerField(default=0)),
                ("synced_at", models.DateTimeField(blank=True, null=True)),
                ("last_error", models.TextField(blank=True)),
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
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offline_scans",
                        to="mobile.deviceregistration",
                    ),
                ),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.AddIndex(
            model_name="offlinescanqueue",
            index=models.Index(fields=["sync_status", "created_at"], name="mobile_offl_sync_p10_idx"),
        ),
    ]
