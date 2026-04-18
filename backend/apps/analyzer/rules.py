"""Rule-based detection layer (regex + keywords) for fast, deterministic flagging."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Each rule maps to a category and a *baseline* risk level if matched.
# Multilingual keywords (English / Arabic / French) are included where useful.
RULES: list[dict] = [
    # ---------------- RIBA ---------------------------------------------
    {
        "category": "riba",
        "risk": "high",
        "patterns": [
            r"\binterest\s+rate\b",
            r"\bcompound(?:ed)?\s+interest\b",
            r"\bAPR\b",
            r"\bannual\s+percentage\s+rate\b",
            r"\bdefault\s+interest\b",
            r"\busury\b",
            r"\bفائدة\b",            # Arabic: interest
            r"\bربا\b",               # Arabic: riba
            r"\bintérêt(s)?\b",      # French
            r"\btaux\s+d['’]intérêt\b",
        ],
    },
    {
        "category": "riba",
        "risk": "medium",
        "patterns": [
            r"\blate\s+(?:payment\s+)?(?:fee|penalty|charge)s?\b",
            r"\bpenalty\s+interest\b",
            r"\bovernight\s+rate\b",
            r"\bLIBOR\b",
            r"\bSOFR\b",
            r"\b\d+(?:\.\d+)?\s*%\s*per\s*annum\b",
            r"\bpaiement\s+en\s+retard\b",
        ],
    },
    # ---------------- GHARAR -------------------------------------------
    {
        "category": "gharar",
        "risk": "medium",
        "patterns": [
            r"\bsubject\s+to\s+change\s+without\s+notice\b",
            r"\bat\s+(?:the\s+)?(?:our|company['’]s)\s+sole\s+discretion\b",
            r"\bunspecified\s+(?:price|terms?|quantity)\b",
            r"\bto\s+be\s+determined\b",
            r"\bTBD\b",
            r"\bforce\s+majeure\b",   # often legitimate but worth flagging for review
            r"\bغرر\b",               # Arabic: gharar
            r"\bincertitude\b",       # French
        ],
    },
    # ---------------- MAYSIR -------------------------------------------
    {
        "category": "maysir",
        "risk": "high",
        "patterns": [
            r"\bgambling\b",
            r"\bwager(?:ing)?\b",
            r"\blottery\b",
            r"\bspread[-\s]?bet(?:ting)?\b",
            r"\bderivative\s+speculation\b",
            r"\bbinary\s+option(s)?\b",
            r"\bميسر\b",
            r"\bقمار\b",
            r"\bjeu(x)?\s+de\s+hasard\b",
            r"\bpari(s)?\s+sportif(s)?\b",
        ],
    },
    # ---------------- PROHIBITED industries ----------------------------
    {
        "category": "prohibited",
        "risk": "high",
        "patterns": [
            r"\balcohol(ic)?\b",
            r"\bwine(ry)?\b",
            r"\bbrewery\b",
            r"\bdistillery\b",
            r"\bpork\b",
            r"\bswine\b",
            r"\bcasino\b",
            r"\badult\s+entertainment\b",
            r"\bخمر\b",
            r"\bخنزير\b",
            r"\balcool\b",
            r"\bporc\b",
        ],
    },
]


@dataclass
class RuleHit:
    category: str
    risk: str
    keywords: list[str] = field(default_factory=list)


# Pre-compile once at import time
_COMPILED: list[tuple[dict, list[re.Pattern]]] = [
    (rule, [re.compile(p, re.IGNORECASE | re.UNICODE) for p in rule["patterns"]])
    for rule in RULES
]


def detect(text: str) -> list[RuleHit]:
    """Return rule hits aggregated per category, keeping the strongest risk."""
    by_category: dict[str, RuleHit] = {}
    risk_rank = {"none": 0, "low": 1, "medium": 2, "high": 3}

    for rule, patterns in _COMPILED:
        for pat in patterns:
            for m in pat.finditer(text):
                cat = rule["category"]
                hit = by_category.get(cat)
                if not hit:
                    hit = RuleHit(category=cat, risk=rule["risk"])
                    by_category[cat] = hit
                # Upgrade risk if this rule is stronger
                if risk_rank[rule["risk"]] > risk_rank[hit.risk]:
                    hit.risk = rule["risk"]
                token = m.group(0).strip()
                if token and token.lower() not in (k.lower() for k in hit.keywords):
                    hit.keywords.append(token)

    return list(by_category.values())
