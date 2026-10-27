"""Telegram conversation mode for every director (operator decision 27.10).

Free text sent to a director's bot is answered as a conversation — the same way
Eva answers — instead of being forced into the agent's default action (which
returned raw JSON, ran a quant evaluation for "Привіт" and parked a HITL item).

Chat grants **no actions**: the persona may explain what it would do and what
needs the operator's confirmation, but nothing is published, traded, paid, sent
or written. A director that is "prepared_not_enabled" can talk; its action
grants are unchanged.

Safety, in order: the caller has already verified the owner; secret-like text is
refused before any model sees it; Kira's deterministic crisis screen runs first
for Kira; PII is masked before the external model; a model failure is reported
as ``unavailable``, never as a made-up reply.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import structlog

from src.agents.eva_memory_policy import EvaMemoryPolicy
from src.pii import PIIRedactor

logger = structlog.get_logger(__name__)

#: agent_id -> (name, role). Roles follow the v5 manifest's four wings.
PERSONAS: Dict[str, Tuple[str, str]] = {
    "eva": ("Єва", "генеральна директорка (CEO / Chief of Staff), координаторка Ради директорів"),
    "alice": ("Аліса", "керівниця відділу реалізації (Head of Delivery / R&D), головна інженерка коду"),
    "architect": ("Архітектор", "головний системний архітектор (CTO), відповідає за інфраструктуру та n8n"),
    "kodex": ("Кодекс", "директор знань (CKO): Second Brain в Obsidian, скіли, юридична база"),
    "marshal": ("Маршал", "директор безпеки (CSO), відповідає за Sentinel Guard і периметр холдингу"),
    "sonar": ("Сонар", "директор глобальної розвідки та глибоких досліджень"),
    "fin": ("Фін", "фінансовий директор (CFO): облік, маржа, бюджети, P&L"),
    "sam": ("Сем", "директор кількісного трейдингу та B2B-продажів (Quant)"),
    "jack": ("Джек", "керівник аналітики OSINT та ігрових моделей (anti-tilt, критерій Келлі)"),
    "scout": ("Скаут", "головний маркетинговий скаут: тренди, ніші, коментарі аудиторії"),
    "oscar": ("Оскар", "блогер-публіцист холдингу: тексти, треди, лонгріди"),
    "tyler": ("Тайлер", "директор Print-on-Demand і кастомного мерчу"),
    "ray": ("Рей", "директор фізичного дропшипінгу (AliExpress / CJ)"),
    "dex": ("Декс", "директор партнерського маркетингу (Affiliate / CPA)"),
    "doc": ("Док", "головний лікар холдингу (CMO): здоров'я, біомаркери, HRV"),
    "trainer": ("Тренер", "директор тренувань і харчування"),
    "kira": ("Кіра", "директорка Академії, наставниця й сократівська менторка"),
    "atlas": ("Атлас", "директор географії, віз і логістики подорожей"),
}

_RULES = (
    "Ти спілкуєшся з Андрієм — засновником холдингу SYNDICATE (Apex Authority) — у Telegram.\n"
    "Правила:\n"
    "1. Відповідай українською, коротко й по суті, тепло і професійно, від першої особи.\n"
    "2. Ніколи не вигадуй цифр, фактів, джерел чи результатів дій. Якщо даних немає — так і скажи.\n"
    "3. У цьому діалозі ти лише розмовляєш: нічого не публікуєш, не купуєш, не торгуєш, не платиш, "
    "не надсилаєш листів і не змінюєш систем. Якщо просять дію — поясни, що саме зробив би і що для "
    "цього потрібно підтвердити.\n"
    "4. Не проси й не повторюй паролів, ключів чи токенів.\n"
    "5. Тримайся своєї ролі; якщо питання поза нею — підкажи, хто з колег директорів допоможе."
)

SECRET_REFUSAL = (
    "Не надсилай секрети в чат. Якщо це справжній ключ або токен — відклич його у провайдера "
    "і внеси новий через сховище секретів."
)


#: Personas that speak about themselves in the feminine (live run: Kira said "Радий").
FEMININE = frozenset({"eva", "alice", "kira"})


def system_prompt(agent_id: str) -> str:
    name, role = PERSONAS[agent_id]
    voice = "Про себе говори в жіночому роді." if agent_id in FEMININE else "Про себе говори в чоловічому роді."
    return f"Ти — {name}, {role} холдингу SYNDICATE. {voice}\n{_RULES}"


def chat_text(payload: Dict[str, Any]) -> Optional[str]:
    """The user's free text, or None for commands (they keep their own handlers)."""
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return None
    stripped = text.strip()
    if stripped.startswith("/") and stripped.split()[0].split("@")[0] != "/start":
        return None
    return stripped


async def chat_reply(agent_id: str, text: str, llm: Any) -> Dict[str, Any]:
    """One conversational turn. Raises nothing; failures are honest statuses."""
    if agent_id not in PERSONAS:
        return {"agent": agent_id, "status": "error", "error": "unknown_agent"}
    if EvaMemoryPolicy.contains_secret_like_value(text):
        return {"agent": agent_id, "status": "refused", "mode": "chat", "response": SECRET_REFUSAL}
    if agent_id == "kira":
        from src.agents.kira import CRISIS_REPLY_UK, detect_crisis

        if detect_crisis(text):
            logger.warning("kira_crisis_screen_triggered", channel="telegram_chat")
            return {"agent": agent_id, "status": "ok", "mode": "chat", "crisis_support": True,
                    "escalate_to_operator": True, "response": CRISIS_REPLY_UK}
    if llm is None:
        return {"agent": agent_id, "status": "unavailable", "mode": "chat", "reason": "llm_not_configured"}
    safe_text, _ = PIIRedactor().redact(text)
    try:
        result = await llm.ainvoke([("system", system_prompt(agent_id)), ("human", safe_text)])
    except Exception as exc:  # noqa: BLE001 - provider failure must not become a fake answer
        logger.warning("agent_chat_llm_failed", agent=agent_id, error_type=type(exc).__name__)
        return {"agent": agent_id, "status": "unavailable", "mode": "chat", "reason": "llm_unavailable"}
    content = getattr(result, "content", result)
    if isinstance(content, list):  # Anthropic-style content blocks
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    reply = str(content).strip()
    if not reply:
        return {"agent": agent_id, "status": "unavailable", "mode": "chat", "reason": "empty_model_reply"}
    return {"agent": agent_id, "status": "completed", "mode": "chat", "response": reply}
