"""Док — правила бази знань: домени, джерела, допуск фактів, тижневе оновлення.

Чистий Python. Не викликає мережі і не пише в архів. Визначає, що можна зберігати як знання,
а що ні. Базу знань будують окремі дешеві/безкоштовні LLM офлайн-пакетами (не рантайм Дока).
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

# ---------------------------------------------------------------- домени
DOMAINS: Dict[str, Dict[str, str]] = {
    "andrii_medical_vault": {"owner": "andrii", "doc_access": "read_only", "label": "Медичний архів Андрія [ANDRII_IMMUTABLE]"},
    "training_protocols": {"owner": "doc", "doc_access": "read_write", "label": "Тренування і реабілітація"},
    "exercise_library": {"owner": "doc", "doc_access": "read_write", "label": "База вправ"},
    "nutrition_recipes": {"owner": "doc", "doc_access": "read_write", "label": "Рецепти і КБЖУ"},
    "supplements_safety": {"owner": "doc", "doc_access": "read_write", "label": "Добавки і взаємодії"},
    "evidence_research": {"owner": "doc", "doc_access": "read_write", "label": "Дослідження (кеш)"},
    "books": {"owner": "doc", "doc_access": "read_write", "label": "Книжки → база знань"},
}

# ---------------------------------------------------------------- джерела
# Тільки ці хости дозволені для тижневого оновлення. Інше — відмова.
ALLOWED_REFRESH_HOSTS = frozenset({
    "pubmed.ncbi.nlm.nih.gov", "www.cochranelibrary.com", "cochranelibrary.com",
    "www.cdc.gov", "cdc.gov", "www.mayoclinic.org", "moz.gov.ua", "www.moz.gov.ua",
    "www.uptodate.com", "uptodate.com",
})
# Рівень довіри: A — систематичні огляди/клінічні протоколи; B — рецензовані статті;
# C — блоги, канали, книги без рецензії (лише тренування/кухня, не медичні твердження).
SOURCE_TIERS = {"cochrane": "A", "pubmed": "B", "cdc": "A", "mayo": "A", "moz": "A",
                "uptodate": "A", "book": "C", "youtube": "C", "blog": "C"}

# ---------------------------------------------------------------- фільтр шуму
PSEUDOSCIENCE_MARKERS = (
    "детокс", "шлак", "токсин", "детокс-крапельниц", "гомеопат", "цукор гірший за героїн",
    "очищення організму", "чудодійн",
)


def is_pseudoscience(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in PSEUDOSCIENCE_MARKERS)


def admit_fact(record: Dict[str, Any]) -> Dict[str, Any]:
    """Чи можна зберегти як знання. Медичне твердження без джерела рівня A/B не проходить."""
    text = str(record.get("claim", "")).strip()
    if not text:
        return {"status": "rejected", "reason": "empty_claim"}
    if is_pseudoscience(text):
        return {"status": "rejected", "reason": "pseudoscience_marker"}
    domain = record.get("domain")
    if domain not in DOMAINS:
        return {"status": "rejected", "reason": "unknown_domain"}
    if domain == "andrii_medical_vault":
        # Архів Андрія не редагується Доком; лише читання.
        return {"status": "rejected", "reason": "vault_is_read_only_for_doc"}
    tier = SOURCE_TIERS.get(record.get("source_type", ""), "C")
    medical = domain in {"supplements_safety", "evidence_research"} or record.get("medical", False)
    if medical:
        if tier in {"A", "B"} and record.get("evidence_level") in {"1A", "1B"} and record.get("source_url"):
            return {"status": "admitted", "tier": tier}
        if record.get("verified_by") == "andrii":
            return {"status": "admitted", "tier": tier, "verified_by": "andrii"}
        return {"status": "pending_review", "tier": tier, "reason": "medical_needs_tier_AB_or_andrii"}
    return {"status": "admitted", "tier": tier}


def refresh_host_allowed(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return False
    return host in ALLOWED_REFRESH_HOSTS


def weekly_refresh_due(today: date) -> bool:
    """Оновлення бази знань — щонеділі (досьє + ваше доручення)."""
    return today.weekday() == 6


def missing_profile_fields(profile: Dict[str, Any], required: Iterable[str]) -> List[str]:
    """Медичні поля, яких немає у верифікованій картці. Вигадувати не можна."""
    return [f for f in required if profile.get(f) in (None, "")]


def medical_card_status(profile: Dict[str, Any]) -> str:
    """Статус медичної картки: `not_configured`, доки Андрій не верифікував."""
    if profile.get("verified_by") != "andrii":
        return "not_configured"
    return "verified"


def can_store_self_learning(record: Dict[str, Any], today: Optional[date] = None) -> bool:
    """Самонавчання: факт іде в базу зі статусом `pending_review`, доки не пройшов правило допуску."""
    return admit_fact(record)["status"] in {"admitted", "pending_review"}
