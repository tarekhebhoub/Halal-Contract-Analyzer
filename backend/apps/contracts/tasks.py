"""Celery tasks for async pipeline."""
from __future__ import annotations

from celery import shared_task

from .services import process_contract


@shared_task(bind=True, max_retries=2, default_retry_delay=15)
def process_contract_task(self, contract_id: str):
    try:
        process_contract(contract_id)
    except Exception as exc:  # pragma: no cover
        raise self.retry(exc=exc)
