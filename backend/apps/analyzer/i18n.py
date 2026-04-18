"""Localized strings & explanation templates (EN / AR).

We keep this in a small dict-based module rather than gettext to avoid the
extra build/compile step. Add new languages by extending the maps.
"""
from __future__ import annotations

SUPPORTED = ("en", "ar")
DEFAULT = "en"


def lang(code: str | None) -> str:
    code = (code or "").lower()
    return code if code in SUPPORTED else DEFAULT


# Category labels
CATEGORY_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "riba": "Riba (interest / usury)",
        "gharar": "Gharar (excessive uncertainty)",
        "maysir": "Maysir (gambling / speculation)",
        "prohibited": "Prohibited activity / industry",
    },
    "ar": {
        "riba": "الربا (الفائدة / الاستغلال المالي)",
        "gharar": "الغرر (الغموض المفرط)",
        "maysir": "الميسر (القمار / المضاربة)",
        "prohibited": "نشاط أو صناعة محظورة",
    },
}

# Per-category "why it matters" rationale (NEUTRAL, NOT a ruling)
CATEGORY_RATIONALE: dict[str, dict[str, str]] = {
    "en": {
        "riba": (
            "Classical Islamic finance distinguishes between profit earned through "
            "real economic activity (trade, leasing, partnership) and a fixed cost of "
            "money (interest). Clauses that fix a guaranteed return on a loan, charge "
            "compound interest, or impose punitive late-payment interest are commonly "
            "flagged as potential riba indicators."
        ),
        "gharar": (
            "Contracts in Islamic finance are expected to have clearly defined subject "
            "matter, price, delivery and obligations. Open-ended discretion, undefined "
            "amounts, or terms 'subject to change without notice' introduce *gharar* "
            "(excessive uncertainty) that scholars often consider problematic."
        ),
        "maysir": (
            "Pure speculation, wagering on uncertain outcomes, and zero-sum bets are "
            "classically associated with *maysir*. Derivatives used for pure "
            "speculation, spread-betting, and lotteries typically fall under this "
            "concern."
        ),
        "prohibited": (
            "Funding, distributing, or otherwise enabling activities that Islamic law "
            "considers impermissible — alcohol, pork, gambling venues, adult "
            "entertainment, conventional insurance — is generally treated as a "
            "compliance concern even when the legal contract itself is otherwise "
            "well-structured."
        ),
    },
    "ar": {
        "riba": (
            "تُفرّق مبادئ التمويل الإسلامي الكلاسيكية بين الربح الناتج عن نشاط اقتصادي "
            "حقيقي (تجارة، إيجار، مشاركة) وبين تكلفة ثابتة على المال (الفائدة). البنود "
            "التي تُحدِّد عائدًا مضمونًا على القرض أو تفرض فائدة مركّبة أو غرامات تأخير "
            "ربوية كثيرًا ما تُصنَّف كمؤشرات محتملة على الربا."
        ),
        "gharar": (
            "يُتوقَّع في العقود وفق الأحكام الإسلامية أن يكون المحل والثمن والتسليم "
            "والالتزامات محدّدةً بوضوح. ترك صلاحيات مفتوحة، أو مبالغ غير محدّدة، أو "
            "بنود «قابلة للتغيير دون إشعار» يُدخل غررًا قد يعتبره العلماء إشكاليًا."
        ),
        "maysir": (
            "ترتبط المضاربة الصرفة والمراهنات على نتائج غير مؤكدة والرهانات الصفرية "
            "تقليديًا بمفهوم الميسر. وتدخل عادةً ضمن هذا المؤشر المشتقّاتُ المستخدمة "
            "للمضاربة البحتة، والمراهنات على الفروقات، واليانصيب."
        ),
        "prohibited": (
            "تمويل أو توزيع أو تمكين أنشطة تعتبرها الشريعة محظورة — كالخمور ولحم "
            "الخنزير، ودور القمار، والترفيه للبالغين، والتأمين التجاري التقليدي — "
            "يُعَدّ عادةً مؤشّر مخاطر امتثالية حتى لو كان العقد القانوني نفسه سليمًا "
            "من ناحية الصياغة."
        ),
    },
}

# Template fragments
T = {
    "en": {
        "header": "🔎 **Potential {label} indicator detected.**",
        "what": "**What was detected:** ",
        "rule": "Rule-based pattern matched on: {kw}.",
        "llm": "Contextual review by the AI assistant: {reason}",
        "why": "**Why this matters:** {rationale}",
        "recommend": (
            "**Recommended next step:** Have a qualified scholar or your "
            "Sharia advisory board review this clause in the context of the full "
            "contract before signing or executing."
        ),
        "evidence_intro": "**Classical references commonly cited on this topic:**",
        "disclaimer": (
            "⚖️ This is a *potential compliance risk* indicator — not a religious "
            "ruling. The platform never issues fatwas."
        ),
    },
    "ar": {
        "header": "🔎 **رُصد مؤشر محتمل على {label}.**",
        "what": "**ما تم رصده:** ",
        "rule": "تطابق نمط قاعدي على: {kw}.",
        "llm": "مراجعة سياقية بواسطة المساعد الذكي: {reason}",
        "why": "**لماذا يستوجب الانتباه:** {rationale}",
        "recommend": (
            "**الخطوة الموصى بها:** يُنصَح بعرض هذا البند على عالم مؤهَّل أو على الهيئة "
            "الشرعية لديك لمراجعته في سياق العقد كاملًا قبل التوقيع أو التنفيذ."
        ),
        "evidence_intro": "**مراجع كلاسيكية يُستشهد بها عادةً في هذا الموضوع:**",
        "disclaimer": (
            "⚖️ هذا مؤشر *احتمالي* لمخاطر الامتثال وليس فتوى شرعية. المنصّة لا تصدر "
            "أحكامًا شرعية."
        ),
    },
}


def category_label(category: str, language: str) -> str:
    return CATEGORY_LABELS[lang(language)].get(category, category)


def category_rationale(category: str, language: str) -> str:
    return CATEGORY_RATIONALE[lang(language)].get(category, "")


def t(key: str, language: str) -> str:
    return T[lang(language)].get(key, T[DEFAULT].get(key, ""))
