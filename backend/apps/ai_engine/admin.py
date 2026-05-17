from django.contrib import admin

from apps.ai_engine.models import AIRiskAssessment


@admin.register(AIRiskAssessment)
class AIRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("assessment_type", "risk_level", "risk_score", "model_version", "created_at")
    list_filter = ("assessment_type", "risk_level", "model_version")
