"""Serializers for contracts/clauses/analysis."""
from rest_framework import serializers
from django.conf import settings

from .models import AnalysisResult, Clause, Contract


class ClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clause
        fields = (
            "id",
            "position",
            "text",
            "char_start",
            "char_end",
            "risk_level",
            "category",
            "explanation",
            "confidence",
            "matched_keywords",
            "evidences",
        )


class AnalysisResultSerializer(serializers.ModelSerializer):
    disclaimer = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisResult
        fields = (
            "risk_score",
            "summary",
            "category_breakdown",
            "high_risk_count",
            "medium_risk_count",
            "low_risk_count",
            "clauses_count",
            "engine_version",
            "created_at",
            "updated_at",
            "disclaimer",
        )

    def get_disclaimer(self, _) -> str:
        return settings.DISCLAIMER


class ContractListSerializer(serializers.ModelSerializer):
    risk_score = serializers.IntegerField(source="analysis.risk_score", read_only=True, default=None)

    class Meta:
        model = Contract
        fields = (
            "id",
            "title",
            "status",
            "language",
            "size_bytes",
            "mime_type",
            "risk_score",
            "created_at",
        )


class ContractDetailSerializer(serializers.ModelSerializer):
    clauses = ClauseSerializer(many=True, read_only=True)
    analysis = AnalysisResultSerializer(read_only=True)
    disclaimer = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = (
            "id",
            "title",
            "status",
            "language",
            "size_bytes",
            "mime_type",
            "raw_text",
            "error_message",
            "created_at",
            "updated_at",
            "clauses",
            "analysis",
            "disclaimer",
        )

    def get_disclaimer(self, _) -> str:
        return settings.DISCLAIMER


class ContractUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    title = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Contract
        fields = ("id", "title", "file", "language")
        read_only_fields = ("id",)
