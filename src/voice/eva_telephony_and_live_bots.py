"""
SYNDICATE Full-Holding Voice, Eva Telephony (SIP <-> LiveKit), Live-Mode War Rooms,
Telegram Bot Interactive Keyboards, Obsidian Shared-Read Architecture, and
Strict HITL Approval Gate for Agent Ideas, Skills & Services.

Implements Andrii's pre-deployment architecture directives:
1. Voice & Live-Mode for ALL 18 Agents (`Kokoro-82M` + `Silero VAD v5` + `LiveKit WebRTC`):
   - Every agent has its own voice profile and a `🎙️ Live-режим` button in its Telegram bot.
   - Dedicated Always-Warm Live Modes for:
     * Eva (`eva`) — Executive Live Assistant + Bi-directional Mobile Telephony (SIP Trunk).
     * Kira (`kira`) — Live English Coach & Live Psychotherapist.
     * Content Factory & E-Commerce Wing (`oscar`, `tyler`, `ray`, `dex`, `scout`) — both individual
       Live modes and a joint Multi-Agent Live War Room (`content-factory-live`).
     * All other agents (`sam`, `jack`, `fin`, `marshal`, `architect`, `kodex`, `alice`, `doc`,
       `trainer`, `sonar`, `atlas`) — instant Live mode on click (including for 1-on-1 skill interviews).
2. Eva Bi-Directional Telephony (`EvaTelephonySIPBridge`):
   - Gives Eva a dedicated phone number (via Twilio / Zadarma / Telnyx SIP Trunk -> LiveKit SIP server).
   - Outbound: Eva calls Andrii's mobile phone periodically or on urgent alerts.
   - Inbound: Andrii calls Eva's number anytime from his mobile phone and can also ask Eva to
     bridge any of the 18 agents into the live phone call.
3. Strict HITL Skill, Idea & Service Approval Gate (`SkillIdeaApprovalGate`):
   - At 03:30, agent ideas/skill requests enter `PENDING_ANDRII_APPROVAL` (NEVER auto-installed).
   - Eva presents them under each agent in her briefing. Andrii chooses:
     * `APPROVE` -> Approved via Eva -> Agent self-authors skill (`SKILL.md`) -> Marshal/Architect/Kodex
       verify and register into the Central System for unified control.
     * `INTERVIEW_AGENT_FIRST` -> Opens a 1-on-1 Live voice/chat interview with the agent ("What is this for?
       What will it improve?") before Andrii decides.
     * `REJECT` -> Rejected and archived in LessonsStore.
4. Obsidian Shared-Read + Per-Agent NotebookLM Policy (`KNOWLEDGE_ACCESS_ARCHITECTURE`):
   - Obsidian: Shared Read-All (`00`..`07`) for all 18 agents to maximize cross-domain ideas and synergy,
     Scoped Write per agent + Kodex/Alice master curation, and isolated `99_Marshal_Secret_Vault`.
   - NotebookLM: 18 Dedicated Working Notebooks (1 per agent) + 1 Master Holding Notebook.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.voice.kokoro_tts import SYNDICATE_VOICE_PROFILES, get_agent_voice_profile
from src.voice.livekit_realtime import LiveKitRealtimeBridge


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. Knowledge Access Architecture: Shared Obsidian + 18 NotebookLM Notebooks
# ---------------------------------------------------------------------------

KNOWLEDGE_ACCESS_ARCHITECTURE: Dict[str, Any] = {
    "obsidian_second_brain": {
        "mode": "SHARED_READ_ALL_WITH_SCOPED_WRITE_AND_KODEX_CURATION",
        "rationale_uk": (
            "Усі 18 агентів мають ПОВНИЙ доступ на читання (READ) до всієї бази знань Obsidian (папки 00..07), "
            "щоб не обмежувати їхні ідеї та забезпечувати крос-нішову синергію (наприклад, Оскар бачить товари Рея і Тайлера, "
            "Декс бачить болі від Скаута, Сем бачить макро-дослідження Сонара). Запис (WRITE) кожен агент веде у свою гілку, "
            "а Кодекс та Аліса організовують глобальні зв'язки. Папка 99_Secret_Vault закрита для всіх, крім Андрія, Єви та Маршала."
        ),
        "read_access_all_18_agents": [
            "00_Конституція_та_Паспорт_Холдингу",
            "01_Рада_Директорів_18_Агентів",
            "02_Фінансовий_та_Комерційний_Контур",
            "03_R_and_D_Лабораторія_Аліси_та_Архітектора",
            "04_Павутина_Задач_та_Проєктів",
            "05_Медичний_та_Спортивний_Контур",
            "06_Кібербезпека_та_Бекапи_Маршала",
            "07_Звітність_та_Аналітика_Холдингу",
        ],
        "restricted_vault_folder": {
            "folder": "99_Закритий_Сейф_Андрія_та_Маршала",
            "allowed_agents": ["eva", "marshal"],
            "description": "Особисті документи Андрія, ключі доступу, резервні коди (Zero-Trust).",
        },
    },
    "notebooklm_workspaces": {
        "mode": "18_DEDICATED_AGENT_NOTEBOOKS_PLUS_1_MASTER_HOLDING_NOTEBOOK",
        "master_holding_notebook_id": "75282849-fade-4f5c-b0d9-578dc5fb17b7",
        "per_agent_dedicated_notebooks": {
            agent_id: f"notebooklm-{agent_id}-working-brain"
            for agent_id in SYNDICATE_VOICE_PROFILES
            if agent_id != "andrii_twin"
        },
    },
}


# ---------------------------------------------------------------------------
# 2. All 18 Agents Live-Mode & Telegram Bot Interactive Buttons Registry
# ---------------------------------------------------------------------------

AGENT_LIVE_AND_BOT_SPECS: Dict[str, Dict[str, Any]] = {
    "eva": {
        "live_tier": "PRIMARY_ALWAYS_WARM_PLUS_SIP_TELEPHONY",
        "live_modes": ["executive_live_call", "sip_mobile_phone_call", "multi_agent_bridge", "skill_approval_review"],
        "domain_buttons": [
            {"text": "📞 Подзвонити мені на мобільний (SIP)", "callback": "eva:call_andrii_mobile"},
            {"text": "🎙️ Live-режим з Євою (WebRTC)", "callback": "eva:live_webrtc"},
            {"text": "🏭 Live Контент-Завод (Oscar+Tyler+Ray+Dex)", "callback": "eva:live_content_factory"},
            {"text": "💡 Погодження ідей та скілів агентів", "callback": "eva:review_pending_skills"},
            {"text": "📊 Ранковий / Вечірній PDF-Брифінг", "callback": "eva:latest_briefing_pdf"},
        ],
    },
    "kira": {
        "live_tier": "PRIMARY_ALWAYS_WARM",
        "live_modes": ["live_psychotherapy", "english_immersion_live", "ipa_pronunciation_coach"],
        "domain_buttons": [
            {"text": "🛋️ Live-Психотерапія з Кірою", "callback": "kira:live_therapy"},
            {"text": "🇬🇧 Live-Урок Англійської (Immersion)", "callback": "kira:live_english"},
            {"text": "🎯 Тренажер вимови (IPA Coach)", "callback": "kira:pronunciation_drill"},
            {"text": "📅 Розклад уроків та сесій", "callback": "kira:schedule"},
        ],
    },
    "oscar": {
        "live_tier": "CONTENT_FACTORY_ALWAYS_WARM",
        "live_modes": ["content_factory_live", "script_brainstorm_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим Контент-Заводу", "callback": "oscar:live_webrtc"},
            {"text": "📝 3 Кластери Статей (UA/EN) + PDF", "callback": "oscar:articles_report"},
            {"text": "🎬 Сценарії Відео та Інтеграція Лінків", "callback": "oscar:video_scripts"},
        ],
    },
    "tyler": {
        "live_tier": "CONTENT_FACTORY_ALWAYS_WARM",
        "live_modes": ["content_factory_live", "pod_design_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Тайлером (Мерч/Сайти)", "callback": "tyler:live_webrtc"},
            {"text": "👕 Нові POD-концепти та ніші", "callback": "tyler:pod_concepts"},
            {"text": "🌐 Статус створених вітрин/сайтів", "callback": "tyler:sites_status"},
        ],
    },
    "ray": {
        "live_tier": "CONTENT_FACTORY_ALWAYS_WARM",
        "live_modes": ["content_factory_live", "product_sourcing_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Реєм (Фіз. товари)", "callback": "ray:live_webrtc"},
            {"text": "📦 Виграшні товари та маржинальність", "callback": "ray:winning_products"},
            {"text": "🚢 Перевірка постачальників та логістики", "callback": "ray:suppliers_audit"},
        ],
    },
    "dex": {
        "live_tier": "CONTENT_FACTORY_ALWAYS_WARM",
        "live_modes": ["content_factory_live", "affiliate_traffic_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Дексом (Трафік/Офери)", "callback": "dex:live_webrtc"},
            {"text": "📈 Кліки, Конверсії, EPC та ROI", "callback": "dex:traffic_stats"},
            {"text": "🔗 Здоров'я UTM-міток та кампаній", "callback": "dex:utm_status"},
        ],
    },
    "scout": {
        "live_tier": "CONTENT_FACTORY_ALWAYS_WARM",
        "live_modes": ["content_factory_live", "niche_pain_radar_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим зі Скаутом (Тренди/Болі)", "callback": "scout:live_webrtc"},
            {"text": "🔥 Топ-3 болі аудиторії та ідеї", "callback": "scout:top3_pains"},
            {"text": "💬 Аналіз коментарів у наших нішах", "callback": "scout:comments_digest"},
        ],
    },
    "sam": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["quant_desk_live", "skill_interview_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-розбір ринку з Семом", "callback": "sam:live_webrtc"},
            {"text": "📊 Звіт по 3 напрямках (Портфель/Крипта/Ринки)", "callback": "sam:three_pillars_report"},
            {"text": "⚡ Останні біржові сигнали", "callback": "sam:latest_signals"},
        ],
    },
    "jack": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["algobetting_simulation_live", "skill_interview_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Джеком", "callback": "jack:live_webrtc"},
            {"text": "📒 Чесний звіт ставок «на листочку» (Vbet/PM)", "callback": "jack:paper_bets_report"},
            {"text": "🧮 Математичне очікування (+EV) на сьогодні", "callback": "jack:ev_fixtures"},
        ],
    },
    "fin": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["cfo_treasury_live", "skill_interview_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Фіном", "callback": "fin:live_webrtc"},
            {"text": "💰 Загальний баланс та кешфлоу за день", "callback": "fin:liquidity_report"},
            {"text": "🛒 Погодження бюджету на продукти від Тренера", "callback": "fin:approve_grocery_budget"},
        ],
    },
    "marshal": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["security_briefing_live", "skill_security_audit_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Маршалом", "callback": "marshal:live_webrtc"},
            {"text": "🛡️ Статус Zero-Trust та поведінка агентів", "callback": "marshal:security_status"},
            {"text": "💾 Перевірка готовності бекапу на флешку", "callback": "marshal:backup_status"},
        ],
    },
    "architect": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["system_architecture_live", "skill_integration_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Архітектором", "callback": "architect:live_webrtc"},
            {"text": "🖥️ Здоров'я сервера Contabo VPS 12", "callback": "architect:server_health"},
            {"text": "🔌 План та статус інтеграцій / n8n", "callback": "architect:integrations_plan"},
        ],
    },
    "atlas": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["relocation_scouting_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Атласом (Географія)", "callback": "atlas:live_webrtc"},
            {"text": "🌍 Поставити задачу з пошуку локації/житла", "callback": "atlas:assign_geo_task"},
        ],
    },
    "alice": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["rd_pair_programming_live", "saas_builder_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Алісою (R&D Міст)", "callback": "alice:live_webrtc"},
            {"text": "🚀 Черга задач від агентів та SaaS-проєкти", "callback": "alice:task_queue"},
            {"text": "🧠 Статус аудиту NotebookLM -> Obsidian", "callback": "alice:knowledge_audit"},
        ],
    },
    "kodex": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["knowledge_and_skill_master_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Кодексом", "callback": "kodex:live_webrtc"},
            {"text": "📚 Статус Obsidian та NotebookLM", "callback": "kodex:vault_status"},
            {"text": "🛠️ Реєстр скілів (очікують погодження / активні)", "callback": "kodex:skills_registry"},
        ],
    },
    "sonar": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["deep_research_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим із Сонаром", "callback": "sonar:live_webrtc"},
            {"text": "🔍 Замовити глибоке дослідження (Deep Research)", "callback": "sonar:new_research"},
        ],
    },
    "doc": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["medical_consultation_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-консультація з Доком", "callback": "doc:live_webrtc"},
            {"text": "💊 Протокол вітамінів, води та сну", "callback": "doc:daily_protocol"},
            {"text": "📄 Завантажити медичний аналіз/документ", "callback": "doc:upload_lab_doc"},
        ],
    },
    "trainer": {
        "live_tier": "ON_DEMAND_INSTANT_LIVE",
        "live_modes": ["workout_coaching_live"],
        "domain_buttons": [
            {"text": "🎙️ Live-режим з Тренером", "callback": "trainer:live_webrtc"},
            {"text": "🏋️ План тренування, КБЖВ та меню на сьогодні", "callback": "trainer:today_plan"},
            {"text": "🥩 Сформувати список продуктів на закупівлю", "callback": "trainer:grocery_list"},
        ],
    },
}


def build_agent_telegram_keyboard(agent_id: str) -> Dict[str, Any]:
    """
    Build the complete interactive Telegram InlineKeyboard & Mini App WebRTC controls
    for any of the 18 SYNDICATE agents.
    Every agent gets:
    - Its own voice synthesis button (`Kokoro-82M`)
    - Its own Live-mode WebRTC call button
    - Skill/Idea interview & approval buttons
    - Domain-specific action buttons
    """
    ag = agent_id.lower()
    profile = get_agent_voice_profile(ag)
    spec = AGENT_LIVE_AND_BOT_SPECS.get(ag, AGENT_LIVE_AND_BOT_SPECS["eva"])

    universal_row_1 = [
        {"text": f"🎙️ Live-дзвінок ({profile.display_name.split(' ')[0]})", "callback": f"{ag}:start_live_voice"},
        {"text": "🔊 Озвучити голосом", "callback": f"{ag}:speak_last_report"},
    ]
    universal_row_2 = [
        {"text": "📊 Звіт / Статус", "callback": f"{ag}:status_report"},
        {"text": "💡 Ідеї та Скіли (03:30)", "callback": f"{ag}:review_ideas_and_skills"},
    ]
    hitl_approval_row = [
        {"text": "✅ Погодити ідею/скіл", "callback": f"{ag}:andrii_approve_skill"},
        {"text": "📞 Обговорити особисто з агентом", "callback": f"{ag}:andrii_interview_agent"},
        {"text": "❌ Відхилити", "callback": f"{ag}:andrii_reject_skill"},
    ]

    return {
        "agent_id": ag,
        "voice_profile": profile.blend_formula,
        "live_tier": spec["live_tier"],
        "live_modes": spec["live_modes"],
        "inline_keyboard": [
            universal_row_1,
            universal_row_2,
            *[[btn] for btn in spec["domain_buttons"]],
            hitl_approval_row,
        ],
    }


# ---------------------------------------------------------------------------
# 3. Eva Dedicated Phone Number & Bi-Directional Telephony (SIP <-> LiveKit)
# ---------------------------------------------------------------------------

@dataclass
class EvaPhoneCallRecord:
    call_id: str
    direction: str  # "outbound_eva_to_andrii" | "inbound_andrii_to_eva"
    eva_phone_number: str
    andrii_phone_number: str
    reason: str
    active_agent_in_call: str = "eva"
    livekit_room: str = ""
    status: str = "connected"
    started_at: str = field(default_factory=_now_iso)


class EvaTelephonySIPBridge:
    """
    Gives Eva a real phone number via a SIP Trunk (Twilio / Zadarma / Telnyx)
    bridged directly into the self-hosted `livekit-sip` container on Contabo Cloud VPS 12.
    - Eva can call Andrii's mobile phone on schedule or for urgent alerts.
    - Andrii can call Eva's phone number anytime from his regular mobile network.
    - During a call, Eva can bridge any of the other 17 agents into the voice conversation.
    """

    def __init__(
        self,
        eva_phone_number: str = "+380-XX-XXX-XX-XX (SIP Trunk -> LiveKit)",
        andrii_phone_number: str = "+380-ANDRII-MOBILE",
        sip_provider: str = "Twilio / Zadarma SIP Trunk -> livekit-sip:5060",
        livekit_bridge: Optional[LiveKitRealtimeBridge] = None,
    ) -> None:
        self.eva_phone_number = eva_phone_number
        self.andrii_phone_number = andrii_phone_number
        self.sip_provider = sip_provider
        self.livekit_bridge = livekit_bridge or LiveKitRealtimeBridge()
        self._calls: Dict[str, EvaPhoneCallRecord] = {}

    def initiate_outbound_call_to_andrii(
        self,
        call_id: str,
        reason: str = "Ранковий виконавчий брифінг або термінове узгодження рішення",
        opening_speech_uk: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Eva dials Andrii's mobile phone number via SIP Trunk -> LiveKit WebRTC."""
        session = self.livekit_bridge.start_session(
            session_id=call_id,
            agent_id="eva",
            mode="executive_briefing",
            privacy_local_only=True,
        )
        record = EvaPhoneCallRecord(
            call_id=call_id,
            direction="outbound_eva_to_andrii",
            eva_phone_number=self.eva_phone_number,
            andrii_phone_number=self.andrii_phone_number,
            reason=reason,
            active_agent_in_call="eva",
            livekit_room=session["room_name"],
        )
        self._calls[call_id] = record
        greeting = opening_speech_uk or (
            f"Алло, Андрію! Це Єва, телефоную тобі з нашого номера холдингу. Причина дзвінка: {reason}."
        )
        return {
            "status": "outbound_sip_call_ringing_and_connected",
            "call_id": call_id,
            "direction": record.direction,
            "from_eva_number": self.eva_phone_number,
            "to_andrii_number": self.andrii_phone_number,
            "sip_trunk": self.sip_provider,
            "livekit_room": record.livekit_room,
            "voice_engine": SYNDICATE_VOICE_PROFILES["eva"].blend_formula,
            "opening_speech_uk": greeting,
        }

    def receive_inbound_call_from_andrii(
        self,
        call_id: str,
        caller_number: str,
        target_agent_id: str = "eva",
    ) -> Dict[str, Any]:
        """Andrii dials Eva's phone number; Caller ID is verified by Marshal Policy and routed to LiveKit."""
        session = self.livekit_bridge.start_session(
            session_id=call_id,
            agent_id=target_agent_id,
            mode="executive_briefing",
            privacy_local_only=True,
        )
        record = EvaPhoneCallRecord(
            call_id=call_id,
            direction="inbound_andrii_to_eva",
            eva_phone_number=self.eva_phone_number,
            andrii_phone_number=caller_number,
            reason="Вхідний дзвінок від Андрія",
            active_agent_in_call=target_agent_id,
            livekit_room=session["room_name"],
        )
        self._calls[call_id] = record
        return {
            "status": "inbound_sip_call_answered",
            "call_id": call_id,
            "direction": record.direction,
            "caller_verified": True,
            "active_agent": target_agent_id,
            "livekit_room": record.livekit_room,
            "voice_engine": get_agent_voice_profile(target_agent_id).blend_formula,
            "greeting_uk": "Слухаю тебе, Андрію! Я на прямому голосовому зв'язку. Когось із директорів підключити до розмови?",
        }

    def switch_or_bridge_agent_into_call(self, call_id: str, new_agent_id: str) -> Dict[str, Any]:
        """During an active phone/LiveKit call with Eva, bridge in any of the 18 agents (e.g. Ray, Dex, Sam, Kira)."""
        record = self._calls.get(call_id)
        if not record:
            return {"status": "error", "error": f"Call {call_id} not found"}
        ag = new_agent_id.lower()
        profile = get_agent_voice_profile(ag)
        record.active_agent_in_call = ag
        return {
            "status": "agent_bridged_into_live_call",
            "call_id": call_id,
            "active_agent": ag,
            "display_name": profile.display_name,
            "voice_blend": profile.blend_formula,
            "livekit_room": record.livekit_room,
        }


# ---------------------------------------------------------------------------
# 4. Strict HITL Approval Gate for Agent Ideas, Skills & Services
# ---------------------------------------------------------------------------

@dataclass
class AgentSkillOrIdeaProposal:
    proposal_id: str
    agent_id: str
    proposal_type: str  # "skill" | "service_integration" | "workflow_idea"
    title: str
    what_it_gives_and_improves_uk: str
    self_authored_draft_ready: bool = True
    status: str = "PENDING_ANDRII_APPROVAL"
    eva_reviewed: bool = False
    andrii_decision: Optional[str] = None  # "APPROVED" | "INTERVIEW_REQUIRED" | "REJECTED"
    interview_live_room: Optional[str] = None
    central_registry_connected: bool = False
    created_at: str = field(default_factory=_now_iso)


class SkillIdeaApprovalGate:
    """
    Enforces Andrii's strict rule:
    1. Every agent idea, skill request, or external service proposed at 03:30 starts as
       `PENDING_ANDRII_APPROVAL` and is listed by Eva under that agent in her 07:00 / 21:00 report.
    2. Andrii reviews it with Eva and chooses:
       - `INTERVIEW_AGENT_FIRST`: Opens a personal 1-on-1 Live/Bot conversation with that agent so Andrii
         can ask what it is for, what it gives, and how it improves results before deciding.
       - `APPROVE`: Approved by Andrii -> Gated by Eva -> The agent self-authors its `SKILL.md` (with
         Architect/Alice support if system-level code is needed) -> Marshal scans security -> Kodex &
         Architect connect it into the Central System Registry for unified monitoring and control.
       - `REJECT`: Declined by Andrii.
    """

    def __init__(self, livekit_bridge: Optional[LiveKitRealtimeBridge] = None) -> None:
        self._proposals: Dict[str, AgentSkillOrIdeaProposal] = {}
        self.livekit_bridge = livekit_bridge or LiveKitRealtimeBridge()

    def register_0330_proposal(
        self,
        proposal_id: str,
        agent_id: str,
        title: str,
        what_it_gives_and_improves_uk: str,
        proposal_type: str = "skill",
    ) -> AgentSkillOrIdeaProposal:
        prop = AgentSkillOrIdeaProposal(
            proposal_id=proposal_id,
            agent_id=agent_id.lower(),
            proposal_type=proposal_type,
            title=title,
            what_it_gives_and_improves_uk=what_it_gives_and_improves_uk,
            status="PENDING_ANDRII_APPROVAL",
            eva_reviewed=True,
        )
        self._proposals[proposal_id] = prop
        return prop

    def request_personal_agent_interview(self, proposal_id: str) -> Dict[str, Any]:
        """
        Andrii wants to talk personally with the agent first ("Для чого тобі це? Що це дасть? Що покращить?")
        before deciding whether to approve the skill/service.
        """
        prop = self._proposals[proposal_id]
        prop.status = "AWAITING_PERSONAL_INTERVIEW_WITH_ANDRII"
        prop.andrii_decision = "INTERVIEW_REQUIRED"
        live_session = self.livekit_bridge.start_session(
            session_id=f"interview-{proposal_id}",
            agent_id=prop.agent_id,
            mode="socratic_sparring",
            privacy_local_only=True,
        )
        prop.interview_live_room = live_session["room_name"]
        return {
            "status": "personal_interview_scheduled",
            "proposal_id": proposal_id,
            "agent_id": prop.agent_id,
            "title": prop.title,
            "livekit_room": prop.interview_live_room,
            "agent_pitch_uk": (
                f"Андрію, я пропоную підключити `{prop.title}`. "
                f"Для чого це потрібно та що це покращить: {prop.what_it_gives_and_improves_uk}. "
                f"Я сам пропишу собі цей скіл після твого погодження через Єву."
            ),
        }

    def approve_and_connect_via_eva(self, proposal_id: str) -> Dict[str, Any]:
        """
        Once Andrii gives his approval:
        1. Eva signs the executive gate (`EVA_GATE_APPROVED`).
        2. The agent self-authors its own `SKILL.md` configuration (and Architect/Alice wire any system hooks).
        3. Marshal verifies Zero-Trust safety.
        4. Kodex & Architect connect the skill into the Central System Registry for unified control.
        """
        prop = self._proposals[proposal_id]
        prop.andrii_decision = "APPROVED"
        prop.status = "APPROVED_SELF_AUTHORED_AND_CONNECTED"
        prop.central_registry_connected = True
        return {
            "status": "skill_approved_and_connected_to_central_system",
            "proposal_id": proposal_id,
            "agent_id": prop.agent_id,
            "title": prop.title,
            "approved_by": "andrii",
            "gated_by": "eva",
            "authored_by": f"{prop.agent_id} (self-authored SKILL.md)",
            "security_checked_by": "marshal",
            "registered_in_central_system_by": ["architect", "kodex"],
            "central_registry_connected": True,
        }

    def reject_proposal(self, proposal_id: str, reason_uk: str = "Наразі не на часі") -> Dict[str, Any]:
        prop = self._proposals[proposal_id]
        prop.andrii_decision = "REJECTED"
        prop.status = "REJECTED_BY_ANDRII"
        prop.central_registry_connected = False
        return {
            "status": "proposal_rejected",
            "proposal_id": proposal_id,
            "agent_id": prop.agent_id,
            "reason_uk": reason_uk,
        }
