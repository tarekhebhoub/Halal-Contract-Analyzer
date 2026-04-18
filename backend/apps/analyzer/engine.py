"""Hybrid analysis engine: rule-based first, LLM as a refinement layer.

Builds rich, structured, localized explanations (English / Arabic):

  🔎 Header     — what category was detected
  • What was detected (rule-based + LLM contextual review)
  • Why it matters (general scholarly rationale, neutral tone)
  • Recommended next step (consult a scholar)
  • Inline classical references (Quran / Sunnah)
  • Disclaimer

The platform NEVER issues fatwas: every explanation is framed as a
*potential compliance risk*, not a religious ruling.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .evidences import evidences_for
from .i18n import category_label, category_rationale, lang as norm_lang, t
from .llm import LLMResult, analyze as llm_analyze, is_enabled as llm_enabled
from .rules import RuleHit, detect

ENGINE_VERSION = "1.1.0"

RISK_RANK = {"none": 0, "low": 1, "medium": 2, "high": 3}


@dataclass
class ClauseAnalysis:
    risk_level: str = "none"
    category: str = ""
    explanation: str = ""
    confidence: int = 0
    matched_keywords: list[str] = field(default_factory=list)
    evidences: list[dict] = field(default_factory=list)


def analyze_clause(text: str, language: str = "en") -> ClauseAnalysis:
    """Run rules + LLM on a single clause and return a merged verdict."""
    text = (text or "").strip()
    if not text:
        return ClauseAnalysis()

    language = norm_lang(language)
    hits: list[RuleHit] = detect(text)
    rule_hit = _strongest(hits)

    llm_result: LLMResult | None = None
    # Save tokens: skip LLM for very short clauses or pure boilerplate.
    if llm_enabled() and len(text) >= 60:
        llm_result = llm_analyze(text, language=language)

    return _merge(rule_hit, llm_result, hits, language)


def _strongest(hits: list[RuleHit]) -> RuleHit | None:
    if not hits:
        return None
    return max(hits, key=lambda h: RISK_RANK[h.risk])


def _merge(
    rule_hit: RuleHit | None,
    llm_result: LLMResult | None,
    all_hits: list[RuleHit],
    language: str,
) -> ClauseAnalysis:
    # No signal at all
    if not rule_hit and not llm_result:
        return ClauseAnalysis(risk_level="none", explanation="", confidence=0)

    # Pick category: prefer rules (high precision) unless rules are silent.
    category = (rule_hit.category if rule_hit else "") or (llm_result.category if llm_result else "")
    rule_risk = rule_hit.risk if rule_hit else "none"
    llm_risk = llm_result.risk_level if llm_result else "none"

    # Combine risk: take the max so we err on the side of caution, BUT if the
    # LLM strongly disagrees ("none" with high confidence) and the rule was a
    # weak match, downgrade by one level.
    risk = _max_risk(rule_risk, llm_risk)
    if (
        rule_hit and llm_result
        and llm_result.risk_level == "none"
        and llm_result.confidence >= 80
        and RISK_RANK[rule_risk] <= 2
    ):
        risk = _downgrade(rule_risk)

    # Confidence: weighted average favouring agreement
    if rule_hit and llm_result and rule_hit.category == llm_result.category:
        confidence = min(100, 60 + llm_result.confidence // 3)
    elif llm_result:
        confidence = llm_result.confidence
    elif rule_hit:
        confidence = {"low": 45, "medium": 65, "high": 85}.get(rule_hit.risk, 30)
    else:
        confidence = 0

    # Aggregate keywords
    keywords: list[str] = []
    for h in all_hits:
        keywords.extend(h.keywords)
    seen: set[str] = set()
    keywords = [k for k in keywords if not (k.lower() in seen or seen.add(k.lower()))]

    evidences = evidences_for(category, language=language) if category else []
    explanation = _build_explanation(
        category=category,
        risk=risk,
        rule_hit=rule_hit,
        llm_result=llm_result,
        evidences=evidences,
        language=language,
    )

    return ClauseAnalysis(
        risk_level=risk,
        category=category,
        explanation=explanation,
        confidence=confidence,
        matched_keywords=keywords[:25],
        evidences=evidences,
    )


def _build_explanation(
    *,
    category: str,
    risk: str,
    rule_hit: RuleHit | None,
    llm_result: LLMResult | None,
    evidences: list[dict],
    language: str,
) -> str:
    """Compose a multi-section, markdown-friendly explanation."""
    label = category_label(category, language) if category else ""
    parts: list[str] = []

    # Header
    if label:
        parts.append(t("header", language).format(label=label))

    # What was detected
    detected_lines: list[str] = []
    if rule_hit and rule_hit.keywords:
        kw = ", ".join(f"“{k}”" for k in rule_hit.keywords[:6])
        detected_lines.append("• " + t("rule", language).format(kw=kw))
    if llm_result and llm_result.reason:
        detected_lines.append("• " + t("llm", language).format(reason=llm_result.reason))
    if detected_lines:
        parts.append(t("what", language) + "\n" + "\n".join(detected_lines))

    # Why it matters
    rationale = category_rationale(category, language) if category else ""
    if rationale:
        parts.append(t("why", language).format(rationale=rationale))

    # Recommendation
    parts.append(t("recommend", language))

    # Evidences inline (truncated)
    if evidences:
        ev_lines = [t("evidence_intro", language)]
        for ev in evidences:
            ev_lines.append(
                f"• *{ev['source']} — {ev['reference']}*: {ev['text']}"
            )
        parts.append("\n".join(ev_lines))

    # Disclaimer
    parts.append(t("disclaimer", language))

    return "\n\n".join(parts)


def _max_risk(a: str, b: str) -> str:
    return a if RISK_RANK.get(a, 0) >= RISK_RANK.get(b, 0) else b


def _downgrade(risk: str) -> str:
    order = ["none", "low", "medium", "high"]
    idx = order.index(risk) if risk in order else 0
    return order[max(0, idx - 1)]
