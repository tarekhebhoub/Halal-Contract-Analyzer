from django.contrib import admin
from .models import AnalysisResult, Clause, Contract


class ClauseInline(admin.TabularInline):
    model = Clause
    extra = 0
    fields = ("position", "risk_level", "category", "confidence")
    readonly_fields = fields


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "language", "created_at")
    list_filter = ("status", "language")
    search_fields = ("title", "owner__email")
    inlines = [ClauseInline]


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ("contract", "risk_score", "high_risk_count", "medium_risk_count", "created_at")
