from django.contrib import admin

from apps.market_intelligence.models import (
    MarketShortageSignal,
    MedicinePriceIndex,
    PriceManipulationAlert,
    RegionalPriceVariance,
    SubsidyTrackingRecord,
)

admin.site.register(MedicinePriceIndex)
admin.site.register(RegionalPriceVariance)
admin.site.register(MarketShortageSignal)
admin.site.register(PriceManipulationAlert)
admin.site.register(SubsidyTrackingRecord)
