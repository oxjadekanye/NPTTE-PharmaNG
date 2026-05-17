from django.contrib import admin

from apps.emergency_response.models import (
    CrisisDistributionPlan,
    EmergencyMedicineAllocation,
    EmergencyStockTransfer,
    NationalEmergencyProtocol,
)

admin.site.register(NationalEmergencyProtocol)
admin.site.register(EmergencyMedicineAllocation)
admin.site.register(CrisisDistributionPlan)
admin.site.register(EmergencyStockTransfer)
