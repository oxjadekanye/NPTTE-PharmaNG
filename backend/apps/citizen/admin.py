from django.contrib import admin

from apps.citizen.models import CitizenFraudReport, CitizenVerificationSession, PublicRecallNotice, VerificationHistory

admin.site.register(CitizenVerificationSession)
admin.site.register(VerificationHistory)
admin.site.register(CitizenFraudReport)
admin.site.register(PublicRecallNotice)
