"""Text extraction.

Currently restricted to plain text (.txt) to keep memory and CPU usage minimal.
PDF/DOCX support has been intentionally removed.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text(path: str | Path, mime_type: str) -> str:
    """Return raw text from a contract file. Only plain text is supported."""
    p = str(path)
    lower = p.lower()
    if not (lower.endswith(".txt") or (mime_type or "").startswith("text/")):
        raise ValueError(
            "Only plain-text (.txt) contracts are supported in this build."
        )
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except OSError as exc:  # pragma: no cover - defensive
        logger.exception("Failed to read text file: %s", exc)
        raise
