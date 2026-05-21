# Generated for Phase 11 — task notes, evidence refs, completion timestamp

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0001_phase15_operational_persistence"),
    ]

    operations = [
        migrations.AddField(
            model_name="operationaltask",
            name="operational_notes",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="operationaltask",
            name="evidence_refs",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="operationaltask",
            name="completed_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
