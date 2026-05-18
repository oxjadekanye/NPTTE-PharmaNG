# Phase 8 — immutable batch regulatory audit trail

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0004_productbatch_lifecycle_status"),
        ("traceability", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BatchRegulatoryAudit",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("active", "Active"), ("suspended", "Suspended"), ("archived", "Archived")], db_index=True, default="active", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("action", models.CharField(choices=[
                    ("submitted", "Submitted for approval"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("suspended", "Suspended"),
                    ("recalled", "Recalled"),
                    ("serials_issued", "Serials issued"),
                    ("destroyed", "Destroyed"),
                ], db_index=True, max_length=64)),
                ("notes", models.TextField(blank=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="batch_regulatory_audits", to=settings.AUTH_USER_MODEL)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="regulatory_audits", to="products.productbatch")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Batch regulatory audit",
                "verbose_name_plural": "Batch regulatory audits",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="batchregulatoryaudit",
            index=models.Index(fields=["batch", "created_at"], name="traceability_batch_created_idx"),
        ),
    ]
