"""Domain models for contracts, clauses, and analysis results."""
from __future__ import annotations

import uuid
from django.conf import settings
from django.db import models


def contract_upload_path(instance: "Contract", filename: str) -> str:
    return f"contracts/{instance.owner_id}/{instance.id}/{filename}"


class Contract(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        EXTRACTING = "extracting", "Extracting text"
        ANALYZING = "analyzing", "Analyzing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contracts"
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=contract_upload_path)
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    language = models.CharField(max_length=5, default="en")
    raw_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["owner", "-created_at"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} ({self.status})"


class Clause(models.Model):
    class Risk(models.TextChoices):
        NONE = "none", "None"
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="clauses")
    position = models.PositiveIntegerField()
    text = models.TextField()
    char_start = models.PositiveIntegerField(default=0)
    char_end = models.PositiveIntegerField(default=0)
    risk_level = models.CharField(max_length=10, choices=Risk.choices, default=Risk.NONE)
    category = models.CharField(max_length=50, blank=True)  # riba, gharar, maysir, prohibited
    explanation = models.TextField(blank=True)
    confidence = models.PositiveSmallIntegerField(default=0)  # 0-100
    matched_keywords = models.JSONField(default=list, blank=True)
    evidences = models.JSONField(default=list, blank=True)  # list of {source, reference, text}
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("contract", "position")
        indexes = [models.Index(fields=["contract", "position"])]

    def __str__(self) -> str:  # pragma: no cover
        return f"Clause #{self.position} of {self.contract_id}"


class AnalysisResult(models.Model):
    contract = models.OneToOneField(
        Contract, on_delete=models.CASCADE, related_name="analysis"
    )
    risk_score = models.PositiveSmallIntegerField(default=0)  # 0-100
    summary = models.TextField(blank=True)
    category_breakdown = models.JSONField(default=dict, blank=True)
    high_risk_count = models.PositiveIntegerField(default=0)
    medium_risk_count = models.PositiveIntegerField(default=0)
    low_risk_count = models.PositiveIntegerField(default=0)
    clauses_count = models.PositiveIntegerField(default=0)
    engine_version = models.CharField(max_length=20, default="1.0.0")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Analysis({self.contract_id}, score={self.risk_score})"
