"""Aggregate clause-level risks into a single 0-100 contract score, localized."""
from __future__ import annotations

from typing import Iterable

from .i18n import lang as norm_lang

# Weight per risk level — high-risk clauses dominate the score.
WEIGHTS = {"none": 0, "low": 1, "medium": 4, "high": 12}
PER_HIGH_RISK_BOOST = 8
SCORE_CAP = 100


def aggregate_score(clauses: Iterable) -> int:
    """Return a contract-level risk score in [0, 100]."""
    total = 0
    n = 0
    high_count = 0
    for c in clauses:
        n += 1
        risk = getattr(c, "risk_level", "none")
        total += WEIGHTS.get(risk, 0)
        if risk == "high":
            high_count += 1

    if n == 0:
        return 0
    avg = total / n
    score = int(round(avg * 10 + high_count * PER_HIGH_RISK_BOOST))
    return max(0, min(SCORE_CAP, score))


def summarize(clauses: list, score: int, language: str = "en") -> str:
    """Human-readable summary, neutral wording, localized."""
    language = norm_lang(language)
    high = sum(1 for c in clauses if c.risk_level == "high")
    med = sum(1 for c in clauses if c.risk_level == "medium")
    low = sum(1 for c in clauses if c.risk_level == "low")

    if language == "ar":
        if score >= 70:
            verdict = "مخاطر امتثال محتملة مرتفعة"
        elif score >= 40:
            verdict = "مخاطر امتثال محتملة متوسطة"
        elif score >= 15:
            verdict = "مخاطر امتثال محتملة منخفضة"
        else:
            verdict = "مؤشرات مخاطر ضئيلة جدًا"
        return (
            f"يُظهر هذا العقد {verdict} (الدرجة {score}/100): "
            f"{high} بنود عالية المخاطر، {med} متوسطة، {low} منخفضة. "
            "هذه النتائج إشارية فقط ولا تُشكّل حكمًا شرعيًا."
        )

    if score >= 70:
        verdict = "elevated potential compliance risk"
    elif score >= 40:
        verdict = "moderate potential compliance risk"
    elif score >= 15:
        verdict = "low potential compliance risk"
    else:
        verdict = "minimal observed risk indicators"
    return (
        f"This contract shows {verdict} (score {score}/100): "
        f"{high} high, {med} medium, {low} low risk clauses identified. "
        "Findings are indicative only and do not constitute a religious ruling."
    )
