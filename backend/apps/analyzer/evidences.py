"""Curated knowledge base of Quran/Sunnah evidences per category, EN + AR.

These references are widely-cited classical texts used in Islamic finance
literature. They are presented as *educational evidence* — NOT as fatwas.
The platform never declares a clause "haram"; it surfaces *potential
compliance risks* and the textual basis scholars typically rely on.
"""
from __future__ import annotations

EVIDENCES: dict[str, list[dict]] = {
    "riba": [
        {
            "source": "Quran",
            "reference": "Al-Baqarah 2:275",
            "text": {
                "en": (
                    "“Those who consume interest cannot stand [on the Day of Resurrection] "
                    "except as one stands who is being beaten by Satan into insanity. … "
                    "Allah has permitted trade and has forbidden interest (riba).”"
                ),
                "ar": (
                    "﴿الَّذِينَ يَأْكُلُونَ الرِّبَا لَا يَقُومُونَ إِلَّا كَمَا يَقُومُ "
                    "الَّذِي يَتَخَبَّطُهُ الشَّيْطَانُ مِنَ الْمَسِّ ... وَأَحَلَّ اللَّهُ "
                    "الْبَيْعَ وَحَرَّمَ الرِّبَا﴾"
                ),
            },
        },
        {
            "source": "Quran",
            "reference": "Al-Baqarah 2:278-279",
            "text": {
                "en": (
                    "“O you who have believed, fear Allah and give up what remains of riba, "
                    "if you should be believers. And if you do not, then be informed of a war "
                    "from Allah and His Messenger.”"
                ),
                "ar": (
                    "﴿يَا أَيُّهَا الَّذِينَ آمَنُوا اتَّقُوا اللَّهَ وَذَرُوا مَا بَقِيَ مِنَ "
                    "الرِّبَا إِنْ كُنْتُمْ مُؤْمِنِينَ * فَإِنْ لَمْ تَفْعَلُوا فَأْذَنُوا "
                    "بِحَرْبٍ مِنَ اللَّهِ وَرَسُولِهِ﴾"
                ),
            },
        },
        {
            "source": "Sunnah",
            "reference": "Sahih Muslim 1598",
            "text": {
                "en": (
                    "The Prophet ﷺ cursed the one who consumes riba, the one who pays it, "
                    "the one who records it, and the two witnesses to it, saying: "
                    "“They are all alike.”"
                ),
                "ar": (
                    "«لَعَنَ رَسُولُ اللَّهِ ﷺ آكِلَ الرِّبَا وَمُوكِلَهُ وَكَاتِبَهُ "
                    "وَشَاهِدَيْهِ، وَقَالَ: هُمْ سَوَاءٌ» — رواه مسلم"
                ),
            },
        },
    ],
    "gharar": [
        {
            "source": "Sunnah",
            "reference": "Sahih Muslim 1513",
            "text": {
                "en": (
                    "The Messenger of Allah ﷺ forbade the sale involving gharar "
                    "(excessive uncertainty)."
                ),
                "ar": "«نَهَى رَسُولُ اللَّهِ ﷺ عَنْ بَيْعِ الْغَرَرِ» — رواه مسلم",
            },
        },
        {
            "source": "Sunnah",
            "reference": "Sunan Abu Dawud 3376",
            "text": {
                "en": (
                    "He ﷺ forbade the sale of what is not with you, and the sale of what "
                    "you do not own — guarding against unknown outcomes."
                ),
                "ar": (
                    "«نَهَى ﷺ عَنْ بَيْعِ مَا لَيْسَ عِنْدَكَ، وَعَنْ بَيْعِ مَا لَا "
                    "تَمْلِكُ» — رواه أبو داود"
                ),
            },
        },
    ],
    "maysir": [
        {
            "source": "Quran",
            "reference": "Al-Maidah 5:90-91",
            "text": {
                "en": (
                    "“O you who have believed, indeed intoxicants, gambling (maysir), "
                    "[sacrificing on] stone alters [to other than Allah], and divining arrows "
                    "are but defilement from the work of Satan, so avoid it that you may be successful.”"
                ),
                "ar": (
                    "﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِنَّمَا الْخَمْرُ وَالْمَيْسِرُ "
                    "وَالْأَنْصَابُ وَالْأَزْلَامُ رِجْسٌ مِنْ عَمَلِ الشَّيْطَانِ "
                    "فَاجْتَنِبُوهُ لَعَلَّكُمْ تُفْلِحُونَ﴾"
                ),
            },
        },
        {
            "source": "Quran",
            "reference": "Al-Baqarah 2:219",
            "text": {
                "en": (
                    "“They ask you about wine and gambling. Say, ‘In them is great sin and "
                    "[yet, some] benefit for people. But their sin is greater than their benefit.’”"
                ),
                "ar": (
                    "﴿يَسْأَلُونَكَ عَنِ الْخَمْرِ وَالْمَيْسِرِ ۖ قُلْ فِيهِمَا إِثْمٌ "
                    "كَبِيرٌ وَمَنَافِعُ لِلنَّاسِ وَإِثْمُهُمَا أَكْبَرُ مِنْ نَفْعِهِمَا﴾"
                ),
            },
        },
    ],
    "prohibited": [
        {
            "source": "Quran",
            "reference": "Al-Maidah 5:3",
            "text": {
                "en": (
                    "“Forbidden to you are dead animals, blood, the flesh of swine …” — "
                    "used as basis for prohibiting commerce in non-permissible substances."
                ),
                "ar": (
                    "﴿حُرِّمَتْ عَلَيْكُمُ الْمَيْتَةُ وَالدَّمُ وَلَحْمُ الْخِنْزِيرِ...﴾ — "
                    "ويُستدلّ بها على تحريم التجارة في المحرّمات."
                ),
            },
        },
        {
            "source": "Sunnah",
            "reference": "Sunan Abu Dawud 3674",
            "text": {
                "en": (
                    "The Messenger of Allah ﷺ cursed ten persons in connection with wine: "
                    "the producer, distributor, drinker, carrier, the one to whom it is carried, "
                    "the server, the seller, the buyer, the one who consumes its price, "
                    "and the one who orders it."
                ),
                "ar": (
                    "«لَعَنَ رَسُولُ اللَّهِ ﷺ فِي الْخَمْرِ عَشَرَةً: عَاصِرَهَا، "
                    "وَمُعْتَصِرَهَا، وَشَارِبَهَا، وَحَامِلَهَا، وَالْمَحْمُولَةَ إِلَيْهِ، "
                    "وَسَاقِيَهَا، وَبَائِعَهَا، وَآكِلَ ثَمَنِهَا، وَالْمُشْتَرِيَ لَهَا، "
                    "وَالْمُشْتَرَاةَ لَهُ» — رواه أبو داود"
                ),
            },
        },
    ],
}


def evidences_for(category: str, language: str = "en", limit: int = 2) -> list[dict]:
    """Return localized evidences with shape: {source, reference, text}."""
    lang = language if language in ("en", "ar") else "en"
    out: list[dict] = []
    for ev in EVIDENCES.get(category, [])[:limit]:
        text = ev["text"]
        localized = text.get(lang) or text.get("en", "") if isinstance(text, dict) else text
        out.append({
            "source": ev["source"],
            "reference": ev["reference"],
            "text": localized,
        })
    return out
