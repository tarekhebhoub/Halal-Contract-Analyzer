"""Service layer that orchestrates extraction → segmentation → analysis."""
from __future__ import annotations

import logging
from collections import Counter

from django.db import transaction

from apps.analyzer.engine import ENGINE_VERSION, analyze_clause
from apps.analyzer.scoring import aggregate_score, summarize

from .extraction import extract_text
from .models import AnalysisResult, Clause, Contract
from .segmentation import segment_clauses

logger = logging.getLogger(__name__)


@transaction.atomic
def process_contract(contract_id) -> Contract:
    """Run the full pipeline on a contract synchronously."""
    contract = Contract.objects.select_for_update().get(pk=contract_id)
    try:
        contract.status = Contract.Status.EXTRACTING
        contract.save(update_fields=["status", "updated_at"])

        text = extract_text(contract.file.path, contract.mime_type)
        if not text:
            raise ValueError("Could not extract any text from this file.")
        contract.raw_text = text

        contract.status = Contract.Status.ANALYZING
        contract.save(update_fields=["raw_text", "status", "updated_at"])

        # Wipe previous results (idempotent re-runs).
        contract.clauses.all().delete()
        AnalysisResult.objects.filter(contract=contract).delete()

        spans = segment_clauses(text)
        clause_objs: list[Clause] = []
        category_counter: Counter = Counter()

        for span in spans:
            result = analyze_clause(span.text, language=contract.language)
            clause_objs.append(
                Clause(
                    contract=contract,
                    position=span.position,
                    text=span.text,
                    char_start=span.char_start,
                    char_end=span.char_end,
                    risk_level=result.risk_level,
                    category=result.category,
                    explanation=result.explanation,
                    confidence=result.confidence,
                    matched_keywords=result.matched_keywords,
                    evidences=result.evidences,
                )
            )
            if result.category and result.risk_level != Clause.Risk.NONE:
                category_counter[result.category] += 1

        Clause.objects.bulk_create(clause_objs)

        risk_score = aggregate_score(clause_objs)
        AnalysisResult.objects.create(
            contract=contract,
            risk_score=risk_score,
            summary=summarize(clause_objs, risk_score, language=contract.language),
            category_breakdown=dict(category_counter),
            high_risk_count=sum(1 for c in clause_objs if c.risk_level == Clause.Risk.HIGH),
            medium_risk_count=sum(1 for c in clause_objs if c.risk_level == Clause.Risk.MEDIUM),
            low_risk_count=sum(1 for c in clause_objs if c.risk_level == Clause.Risk.LOW),
            clauses_count=len(clause_objs),
            engine_version=ENGINE_VERSION,
        )

        contract.status = Contract.Status.COMPLETED
        contract.error_message = ""
        contract.save(update_fields=["status", "error_message", "updated_at"])
        return contract
    except Exception as exc:
        logger.exception("Contract processing failed for %s", contract_id)
        contract.status = Contract.Status.FAILED
        contract.error_message = str(exc)[:1000]
        contract.save(update_fields=["status", "error_message", "updated_at"])
        raise
