from django.db import models

from apps.core.models import NPTTEBaseModel
from apps.products.models import Product


class EmergencyMedicineWatchlist(NPTTEBaseModel):
    """Critical medicines monitored during national health emergencies."""

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="emergency_watchlist_entries",
    )
    category = models.CharField(
        max_length=64,
        db_index=True,
        help_text="insulin, vaccine, antibiotic, narcotic, controlled, general",
    )
    minimum_national_stock = models.PositiveIntegerField(default=0)
    is_active_watch = models.BooleanField(default=True, db_index=True)
    epidemic_code = models.CharField(max_length=64, blank=True, db_index=True)

    class Meta:
        unique_together = [("product", "epidemic_code")]
        verbose_name = "Emergency medicine watchlist entry"
        verbose_name_plural = "Emergency medicine watchlist"
