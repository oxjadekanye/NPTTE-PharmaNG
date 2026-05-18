# Phase 10 developer API

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
            name="ApiDeveloperKey",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("name", models.CharField(max_length=128)),
                ("key_prefix", models.CharField(db_index=True, max_length=16)),
                ("key_hash", models.CharField(max_length=128, unique=True)),
                ("scopes", models.JSONField(blank=True, default=list)),
                ("is_active_key", models.BooleanField(db_index=True, default=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
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
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="api_keys",
                        to="organisations.organisation",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ApiRequestAudit",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("path", models.CharField(db_index=True, max_length=255)),
                ("method", models.CharField(max_length=16)),
                ("status_code", models.PositiveSmallIntegerField(default=200)),
                ("client_ip", models.GenericIPAddressField(blank=True, null=True)),
                (
                    "api_key",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="request_audits",
                        to="developer_access.apideveloperkey",
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
    ]
