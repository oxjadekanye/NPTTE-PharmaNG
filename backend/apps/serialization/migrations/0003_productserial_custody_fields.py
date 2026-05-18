# Phase 8 — serial custody for pharmacy traceability

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organisations", "0001_initial"),
        ("serialization", "0002_productserial_barcode_payload_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productserial",
            name="custody_organisation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="serials_in_custody",
                to="organisations.organisation",
                help_text="Last pharmacy or supply-chain node that received this serial (Phase 8).",
            ),
        ),
        migrations.AddField(
            model_name="productserial",
            name="custody_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="productserial",
            name="custody_updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="serial_custody_updates",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
