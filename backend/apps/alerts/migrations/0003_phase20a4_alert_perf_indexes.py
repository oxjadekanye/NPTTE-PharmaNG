"""Phase 20A.4 — indexes for open-alert and demo aggregate queries."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alerts", "0002_nationalalertescalation_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="nationalalert",
            index=models.Index(fields=["resolved_at", "created_at"], name="alert_resolved_created_idx"),
        ),
        migrations.AddIndex(
            model_name="nationalalert",
            index=models.Index(fields=["severity", "resolved_at"], name="alert_sev_resolved_idx"),
        ),
    ]
