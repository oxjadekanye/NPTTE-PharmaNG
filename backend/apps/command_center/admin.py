from django.contrib import admin

from apps.command_center.models import (
    EmergencyIntervention,
    NationalIncident,
    NationalThreatAssessment,
    RegionalHealthSignal,
    RegulatoryAction,
    SupplyChainDisruption,
)

admin.site.register(NationalIncident)
admin.site.register(RegionalHealthSignal)
admin.site.register(SupplyChainDisruption)
admin.site.register(EmergencyIntervention)
admin.site.register(RegulatoryAction)
admin.site.register(NationalThreatAssessment)
