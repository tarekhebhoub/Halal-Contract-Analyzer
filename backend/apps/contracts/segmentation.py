"""Clause segmentation using legal-numbering heuristics + sentence fallback."""
from __future__ import annotations

import re
from dataclasses import dataclass

# Matches lines beginning with patterns like "1.", "1.2", "ARTICLE 3", "Section 4 -"
NUMBERED_CLAUSE_RE = re.compile(
    r"(?m)^\s*(?:"
    r"(?:ARTICLE|Article|SECTION|Section|Clause|CLAUSE)\s+\w+[\.\:\-]?"
    r"|(?:\d+(?:\.\d+){0,3})[\.\)\:\-]"
    r"|\([a-zA-Z0-9]{1,3}\)"
    r")\s+"
)


@dataclass
class ClauseSpan:
    position: int
    text: str
    char_start: int
    char_end: int


def segment_clauses(text: str) -> list[ClauseSpan]:
    """Segment a contract into clauses.

    Strategy:
      1. Try splitting on legal numbering / headings.
      2. If too few are found, fall back to paragraph + sentence chunking.
    """
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []

    clauses = list(_segment_by_numbering(text))
    if len(clauses) >= 3:
        return _finalize(clauses)

    # Fallback: paragraphs of meaningful length
    clauses = list(_segment_by_paragraphs(text))
    if len(clauses) >= 3:
        return _finalize(clauses)

    # Final fallback: sentences (NLTK if available, else regex)
    return _finalize(list(_segment_by_sentences(text)))


def _segment_by_numbering(text: str) -> list[ClauseSpan]:
    matches = list(NUMBERED_CLAUSE_RE.finditer(text))
    if not matches:
        return []
    spans: list[ClauseSpan] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        if len(chunk) >= 25:
            spans.append(ClauseSpan(position=i, text=chunk, char_start=start, char_end=end))
    return spans


def _segment_by_paragraphs(text: str) -> list[ClauseSpan]:
    spans: list[ClauseSpan] = []
    cursor = 0
    pos = 0
    for para in re.split(r"\n\s*\n+", text):
        stripped = para.strip()
        if len(stripped) < 40:
            cursor += len(para) + 2
            continue
        start = text.find(stripped, cursor)
        end = start + len(stripped)
        spans.append(ClauseSpan(position=pos, text=stripped, char_start=start, char_end=end))
        pos += 1
        cursor = end
    return spans


def _segment_by_sentences(text: str) -> list[ClauseSpan]:
    try:
        import nltk

        try:
            sentences = nltk.sent_tokenize(text)
        except LookupError:
            nltk.download("punkt", quiet=True)
            sentences = nltk.sent_tokenize(text)
    except Exception:
        sentences = re.split(r"(?<=[\.\!\?])\s+", text)

    spans: list[ClauseSpan] = []
    cursor = 0
    for i, sent in enumerate(sentences):
        s = sent.strip()
        if len(s) < 25:
            continue
        start = text.find(s, cursor)
        if start == -1:
            start = cursor
        end = start + len(s)
        spans.append(ClauseSpan(position=i, text=s, char_start=start, char_end=end))
        cursor = end
    return spans


def _finalize(spans: list[ClauseSpan]) -> list[ClauseSpan]:
    # Re-number contiguously
    return [
        ClauseSpan(position=i, text=s.text, char_start=s.char_start, char_end=s.char_end)
        for i, s in enumerate(spans)
    ]
