"""REST API for contracts and analysis results."""
from __future__ import annotations

import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import Contract
from .reports import build_report
from .serializers import (
    AnalysisResultSerializer,
    ContractDetailSerializer,
    ContractListSerializer,
    ContractUploadSerializer,
)
from .services import process_contract
from .validators import validate_upload

logger = logging.getLogger(__name__)


class ContractViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """CRUD-lite for contracts. Upload uses dedicated action with stricter throttle."""

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"

    def get_queryset(self):
        return (
            Contract.objects.filter(owner=self.request.user)
            .select_related("analysis")
            .prefetch_related("clauses")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ContractDetailSerializer
        if self.action == "upload":
            return ContractUploadSerializer
        return ContractListSerializer

    @action(detail=False, methods=["post"], url_path="upload",
            throttle_classes=[ScopedRateThrottle])
    def upload(self, request):
        self.throttle_scope = "upload"
        serializer = ContractUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload_file = request.FILES.get("file")
        if not upload_file:
            return Response({"detail": "file is required"}, status=400)

        meta = validate_upload(upload_file)
        title = serializer.validated_data.get("title") or upload_file.name
        language = serializer.validated_data.get("language") or request.user.preferred_language

        contract = Contract.objects.create(
            owner=request.user,
            title=title[:255],
            file=upload_file,
            file_hash=meta["sha256"],
            mime_type=meta["mime_type"],
            size_bytes=meta["size_bytes"],
            language=language,
        )

        # Run synchronously when Celery is in eager mode (dev); else dispatch task.
        from django.conf import settings as dj_settings

        if dj_settings.CELERY_TASK_ALWAYS_EAGER:
            try:
                process_contract(contract.id)
            except Exception as exc:
                logger.exception("Inline processing failed: %s", exc)
        else:
            from .tasks import process_contract_task
            process_contract_task.delay(str(contract.id))

        contract.refresh_from_db()
        return Response(
            ContractDetailSerializer(contract).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"], url_path="analysis")
    def analysis(self, request, pk=None):
        contract = self.get_object()
        analysis = getattr(contract, "analysis", None)
        if not analysis:
            return Response({"detail": "Analysis not ready."}, status=202)
        return Response(AnalysisResultSerializer(analysis).data)

    @action(detail=True, methods=["post"], url_path="reprocess")
    def reprocess(self, request, pk=None):
        contract = self.get_object()
        new_lang = request.query_params.get("lang") or request.data.get("lang")
        if new_lang and new_lang in {"en", "ar", "fr"} and new_lang != contract.language:
            contract.language = new_lang
            contract.save(update_fields=["language", "updated_at"])
        from django.conf import settings as dj_settings

        if dj_settings.CELERY_TASK_ALWAYS_EAGER:
            process_contract(contract.id)
        else:
            from .tasks import process_contract_task
            process_contract_task.delay(str(contract.id))
        contract.refresh_from_db()
        return Response(ContractDetailSerializer(contract).data)

    @action(detail=True, methods=["get"], url_path="report")
    def report(self, request, pk=None):
        contract = self.get_object()
        pdf = build_report(contract)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="halal-report-{contract.id}.pdf"'
        )
        return response
