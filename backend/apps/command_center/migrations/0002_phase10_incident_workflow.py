# Phase 10 incident workflow fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("command_center", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="nationalincident",
            name="assigned_investigator",
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.AddField(
            model_name="nationalincident",
            name="escalation_level",
            field=models.PositiveSmallIntegerField(db_index=True, default=1),
        ),
        migrations.AddField(
            model_name="nationalincident",
            name="evidence_lifecycle",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="nationalincident",
            name="workflow_state",
            field=models.CharField(db_index=True, default="open", max_length=64),
        ),
    ]
