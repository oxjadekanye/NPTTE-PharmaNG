from django.contrib import admin

from apps.ai_engine.models import (
    AIRiskAssessment,
    AIRiskSignal,
    CounterfeitHeatmap,
    CounterfeitRiskAssessment,
    DemandForecast,
    DiversionProbability,
    InventoryPrediction,
    MedicineMovementPattern,
    NationalRiskSignal,
    OrganisationRiskScore,
    ShortageForecast,
)


@admin.register(AIRiskAssessment)
class AIRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("assessment_type", "risk_level", "risk_score", "model_version", "created_at")


@admin.register(AIRiskSignal)
class AIRiskSignalAdmin(admin.ModelAdmin):
    list_display = ("signal_type", "score", "organisation", "created_at")


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ("product", "region_state", "forecast_date", "predicted_demand")


@admin.register(InventoryPrediction)
class InventoryPredictionAdmin(admin.ModelAdmin):
    list_display = ("organisation", "product", "shortage_probability")


@admin.register(CounterfeitRiskAssessment)
class CounterfeitRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "probability", "risk_level", "created_at")


@admin.register(OrganisationRiskScore)
class OrganisationRiskScoreAdmin(admin.ModelAdmin):
    list_display = ("organisation", "overall_score", "counterfeit_score", "diversion_score")


admin.site.register(NationalRiskSignal)
admin.site.register(CounterfeitHeatmap)
admin.site.register(DiversionProbability)
admin.site.register(ShortageForecast)
admin.site.register(MedicineMovementPattern)
