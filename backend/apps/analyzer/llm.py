"""LLM client wrapper. Uses OpenAI when configured, otherwise no-op.

Always returns the carefully-worded "potential compliance risk" framing —
never declarative religious rulings. Replies in the requested language.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)


PROMPT_TEMPLATE = """You are an Islamic-finance compliance reviewer assisting a legal team.
You DO NOT issue religious rulings (fatwas). You only flag *potential compliance risks*
relative to widely-cited Islamic finance principles.

Analyze the following contract clause and identify whether it may contain:
- Riba (interest / usury / fixed cost of money)
- Gharar (excessive uncertainty / ambiguous terms)
- Maysir (gambling / pure speculation)
- Prohibited activities (alcohol, pork, gambling, adult entertainment, conventional insurance, etc.)

Respond with STRICT JSON only, no prose, matching this schema:
{{
  "risk_level": "none" | "low" | "medium" | "high",
  "category": "" | "riba" | "gharar" | "maysir" | "prohibited",
  "reason": "<DETAILED factual explanation in {language_name}, 2-4 sentences, neutral tone, no rulings>",
  "confidence": <integer 0-100>
}}

Rules:
- Use "none" if the clause is administrative/standard with no concern.
- Phrase "reason" as a *potential* risk indicator, not a ruling.
- Be specific: cite the exact phrase or mechanism from the clause that triggered the concern,
  and briefly explain WHY it could conflict with the principle.
- The "reason" MUST be written in {language_name}.

Clause:
<<<
{clause}
>>>
"""


LANGUAGE_NAMES = {"en": "English", "ar": "Arabic"}


@dataclass
class LLMResult:
    risk_level: str  # none|low|medium|high
    category: str    # ""|riba|gharar|maysir|prohibited
    reason: str
    confidence: int  # 0-100


def is_enabled() -> bool:
    return bool(settings.LLM_ENABLED and settings.OPENAI_API_KEY)


def analyze(clause_text: str, language: str = "en") -> LLMResult | None:
    """Call the LLM. Returns None on any failure so the rule layer can stand alone."""
    if not is_enabled():
        return None

    try:
        from openai import OpenAI

        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        base_url = (getattr(settings, "OPENAI_BASE_URL", "") or "").strip()
        if base_url:
            client_kwargs["base_url"] = base_url
        # OpenRouter recommends these identification headers; harmless elsewhere.
        if "openrouter" in base_url:
            client_kwargs["default_headers"] = {
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "Halal Contract Analyzer",
            }
        client = OpenAI(**client_kwargs)
        prompt = PROMPT_TEMPLATE.format(
            clause=clause_text[:4000],
            language_name=LANGUAGE_NAMES.get(language, "English"),
        )
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system",
                 "content": "Reply with STRICT JSON. Never declare anything haram."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=600,
            timeout=30,
        )
        content = completion.choices[0].message.content or "{}"
        data = json.loads(content)
        return LLMResult(
            risk_level=_clean_risk(data.get("risk_level", "none")),
            category=_clean_category(data.get("category", "")),
            reason=str(data.get("reason", ""))[:1200],
            confidence=max(0, min(100, int(data.get("confidence", 50)))),
        )
    except Exception as exc:
        logger.warning("LLM analysis failed: %s", exc)
        return None


def _clean_risk(value: str) -> str:
    v = (value or "").lower().strip()
    return v if v in {"none", "low", "medium", "high"} else "none"


def _clean_category(value: str) -> str:
    v = (value or "").lower().strip()
    return v if v in {"riba", "gharar", "maysir", "prohibited"} else ""
