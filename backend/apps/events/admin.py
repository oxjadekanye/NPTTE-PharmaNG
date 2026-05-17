from django.contrib import admin

from apps.events.models import EmergencyEvent, FraudEvent, InventoryEvent, SystemEvent, VerificationEvent

admin.site.register(SystemEvent)
admin.site.register(VerificationEvent)
admin.site.register(InventoryEvent)
admin.site.register(EmergencyEvent)
admin.site.register(FraudEvent)
