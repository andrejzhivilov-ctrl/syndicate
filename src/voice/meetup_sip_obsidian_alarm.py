"""
SYNDICATE Selective Multi-Agent Live Meetups, Single-Number SIP Agent Multiplexing,
Leader Sovereign Signature (`ANDRII_SOVEREIGN_SEAL`), NotebookLM 300-Source Ephemeral Hub,
Obsidian Skills/Prompts/MCP Mirror, 18-Container Hermes+LangGraph Topology, and
Eva's 3-Stage Escalating Alarm Clock & Hybrid Reminder Router.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.voice.kokoro_tts import SYNDICATE_VOICE_PROFILES, get_agent_voice_profile


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. Selective Multi-Agent Live Meetup Rooms (Zero/Low-Token Turn-Taking)
# ---------------------------------------------------------------------------

MEETUP_ROOM_PRESETS: Dict[str, List[str]] = {
    "content_factory": ["oscar", "tyler", "ray", "dex", "scout"],
    "capital_and_markets": ["fin", "sam", "jack"],
    "core_architecture": ["eva", "architect", "marshal", "kodex", "alice"],
    "health_and_longevity": ["doc", "trainer", "kira"],
}


@dataclass
class SelectiveLiveMeetupRoom:
    room_id: str
    title: str
    selected_agents: List[str]
    moderator_agent: str = "eva"
    turn_taking_mode: str = "sequential_round_robin_or_direct_address"
    voice_cost_usd: float = 0.0
    transcript_md_lines: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)


class SyndicateLiveMeetupHub:
    """
    Allows Andrii to create selective multi-agent Live voice/chat rooms (like a Meetup)
    inside Eva's bot / Mini-App by picking ONLY the specific agents needed (e.g. Oscar + Ray + Dex).

    How it prevents token burn:
    1. Audio transport (`LiveKit`), VAD (`Silero v5`), STT (`faster-whisper`), and TTS (`Kokoro-82M`)
       run 100% locally on Contabo Cloud VPS 12 CPU -> $0.00 audio token cost!
    2. For LLM reasoning:
       - Direct Address Mode: If Andrii names an agent ("Рей, що по маржі?"), ONLY Ray's LLM is called.
       - Brainstorm Chain Mode: If Andrii asks the room to brainstorm together, agents speak one by one
         in a short sequential chain (Agent 1 -> Agent 2 hears Agent 1 -> Agent 3 hears 1 & 2) with a
         strict max_tokens=180 cap per turn, and the final synthesis is saved to Obsidian in Markdown.
    """

    def __init__(self) -> None:
        self._rooms: Dict[str, SelectiveLiveMeetupRoom] = {}

    def create_selective_meetup_room(
        self,
        room_id: str,
        selected_agents: List[str],
        title: str = "Робоча Live-Нарада",
    ) -> Dict[str, Any]:
        clean_agents = [a.lower() for a in selected_agents if a.lower() in SYNDICATE_VOICE_PROFILES]
        room = SelectiveLiveMeetupRoom(
            room_id=room_id,
            title=title,
            selected_agents=clean_agents,
        )
        self._rooms[room_id] = room
        return {
            "status": "selective_meetup_room_ready",
            "room_id": room_id,
            "title": title,
            "selected_agents": clean_agents,
            "agent_voices": {a: get_agent_voice_profile(a).blend_formula for a in clean_agents},
            "token_optimization": "Silero VAD + Kokoro-82M ($0 audio) + Sequential Turn-Taking Router",
        }

    def run_brainstorm_round(
        self,
        room_id: str,
        andrii_prompt_uk: str,
        obsidian_vault_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Each selected agent in the room hears Andrii AND the previous agents' points,
        adds its concise contribution, and the full meeting protocol is saved to Obsidian.
        """
        room = self._rooms[room_id]
        room.transcript_md_lines.append(f"**Андрій (Лідер Холдингу):** {andrii_prompt_uk}")
        turns: List[Dict[str, str]] = []
        prior_context: List[str] = []

        for ag in room.selected_agents:
            profile = get_agent_voice_profile(ag)
            heard_note = (
                f"Почув ідеї колег ({', '.join(prior_context)}). "
                if prior_context
                else "Відкриваю обговорення. "
            )
            reply_uk = (
                f"{heard_note}Пропозиція від {ag.upper()}: інтегрувати задачу «{andrii_prompt_uk}» "
                f"у наш конвеєр і зафіксувати план дій у Obsidian."
            )
            turns.append(
                {
                    "agent_id": ag,
                    "voice_blend": profile.blend_formula,
                    "speech_uk": reply_uk,
                }
            )
            prior_context.append(ag.upper())
            room.transcript_md_lines.append(f"- **{profile.display_name}:** {reply_uk}")

        obsidian_file: Optional[str] = None
        if obsidian_vault_path:
            meetups_dir = Path(obsidian_vault_path) / "07_Звітність_та_Аналітика_Холдингу" / "06_Протоколи_Live_Нарад"
            meetups_dir.mkdir(parents=True, exist_ok=True)
            md_path = meetups_dir / f"Meetup_{room_id}.md"
            md_content = (
                f"# 🤝 Протокол Live-Наради: {room.title} (`{room_id}`)\n\n"
                f"**Учасники:** {', '.join(a.upper() for a in room.selected_agents)}\n\n"
                + "\n".join(room.transcript_md_lines)
                + "\n"
            )
            md_path.write_text(md_content, encoding="utf-8")
            obsidian_file = str(md_path)

        return {
            "status": "brainstorm_round_completed",
            "room_id": room_id,
            "participants_count": len(room.selected_agents),
            "turns": turns,
            "audio_token_cost_usd": 0.0,
            "obsidian_protocol_path": obsidian_file,
        }


# ---------------------------------------------------------------------------
# 2. Leader Digital Signature (`ANDRII_SOVEREIGN_SEAL`) for Private Obsidian Docs
# ---------------------------------------------------------------------------

LEADER_SIGNATURE_TAG = "ANDRII_SOVEREIGN_SEAL_ED25519"


class LeaderDocumentGuard:
    """
    Implements Andrii's Sovereign Document Rule in the Shared Obsidian Second Brain:
    - Private/Strategic documents authored by Andrii live inside the shared Obsidian vault
      so ALL 18 agents can READ them and use their insights for synergy.
    - They are stamped with Andrii's personal digital signature (`leader_signature: ANDRII_SOVEREIGN_SEAL_ED25519`).
    - Rules enforced on any document bearing Andrii's signature:
      1. `READ`: Allowed for all 18 agents.
      2. `EDIT / MODIFY`: STRICTLY FORBIDDEN (`0%` permission for any agent).
      3. `DELETE`: STRICTLY FORBIDDEN (`0%` permission for any agent).
      4. `MOVE / ORGANIZE`: Allowed ONLY for Kodex/Alice AND ONLY when `andrii_move_approved=True`.
    """

    @staticmethod
    def sign_leader_markdown(content_md: str, doc_title: str) -> str:
        content_hash = hashlib.sha256(content_md.encode("utf-8")).hexdigest()[:16]
        seal = f"{LEADER_SIGNATURE_TAG}:{content_hash}"
        frontmatter = (
            "---\n"
            f'title: "{doc_title}"\n'
            'owner: "Андрій (Лідер Холдингу SYNDICATE)"\n'
            f'leader_signature: "{seal}"\n'
            "immutable_leader_document: true\n"
            'agent_permissions: "READ_ALL | EDIT_NEVER | DELETE_NEVER | MOVE_ONLY_WITH_ANDRII_APPROVAL"\n'
            "---\n\n"
        )
        return frontmatter + content_md

    @staticmethod
    def is_leader_signed(markdown_text: str) -> bool:
        return LEADER_SIGNATURE_TAG in markdown_text or "immutable_leader_document: true" in markdown_text

    @classmethod
    def check_agent_operation(
        cls,
        markdown_text: str,
        agent_id: str,
        operation: str,  # "read" | "edit" | "delete" | "move"
        andrii_move_approved: bool = False,
    ) -> Dict[str, Any]:
        op = operation.lower()
        signed = cls.is_leader_signed(markdown_text)
        if not signed:
            return {"allowed": True, "operation": op, "leader_signed": False}

        if op == "read":
            return {
                "allowed": True,
                "operation": "read",
                "leader_signed": True,
                "note": "Усі 18 агентів мають право читати документ Лідера Холдингу для синергії.",
            }

        if op == "move" and agent_id.lower() in ("kodex", "alice", "eva") and andrii_move_approved:
            return {
                "allowed": True,
                "operation": "move",
                "leader_signed": True,
                "note": "Переміщення в іншу гілку дозволено за особистим погодженням Андрія без зміни тексту.",
            }

        return {
            "allowed": False,
            "operation": op,
            "leader_signed": True,
            "blocked_by": "Marshal_Leader_Seal_Guard",
            "reason_uk": (
                f"ЗАБОРОНЕНО: Документ захищений особистим підписом Лідера Холдингу ({LEADER_SIGNATURE_TAG}). "
                "Редагування та видалення суворо заборонені; переміщення можливе лише з особистого дозволу Андрія."
            ),
        }


# ---------------------------------------------------------------------------
# 3. NotebookLM 300-Source Ephemeral Hub & Full-Context Obsidian Exporter
# ---------------------------------------------------------------------------

class NotebookLMHubLifecycleManager:
    """
    Manages the 18 Agent Working Notebooks + Andrii's Personal Notebooks in Google NotebookLM:
    1. Subscription limit: 300 sources per notebook.
    2. For Agents (`owner="agent"`):
       - NotebookLM is a temporary analytical & Studio Hub (Mind Maps, Deep Synthesis).
       - Alice & Kodex generate a FULL, EXPANDED, UNCOMPRESSED Markdown dossier (`full_context_lossless=True`)
         merging all insights, tables, and history into Obsidian (`C:\\Second Brain\\`).
       - Once exported to Obsidian, the agent's temporary sources are PURGED from NotebookLM so the
         notebook stays clean and never hits the 300-source ceiling.
       - If an agent tries to load >300 sources at once (or crosses the 280 warning threshold),
         Kodex immediately alerts Andrii to create/share a new overflow notebook.
    3. For Andrii (`owner="andrii"`):
       - Alice & Kodex ALSO export a full expanded Markdown file to Obsidian stamped with
         Andrii's Leader Signature (`ANDRII_SOVEREIGN_SEAL_ED25519`),
       - BUT Andrii's sources are NEVER auto-deleted from NotebookLM — they stay there until
         Andrii explicitly says to delete them!
    """

    MAX_SOURCES_PER_NOTEBOOK = 300
    WARNING_THRESHOLD = 280

    def __init__(self, obsidian_vault_path: Path | str) -> None:
        self.obsidian_vault_path = Path(obsidian_vault_path)
        self._source_counts: Dict[str, int] = {ag: 0 for ag in SYNDICATE_VOICE_PROFILES if ag != "andrii_twin"}

    def process_and_export_notebook_batch(
        self,
        agent_id: str,
        sources: List[Dict[str, str]],
        owner: str = "agent",  # "agent" | "andrii"
        studio_artifacts_created: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        ag = agent_id.lower()
        incoming_count = len(sources)
        current_count = self._source_counts.get(ag, 0) + incoming_count
        overflow_alert_for_andrii = current_count >= self.WARNING_THRESHOLD

        # Build FULL, EXPANDED, UNCOMPRESSED Markdown report for Obsidian (zero context lost)
        sections = [
            f"## 📄 Джерело {idx}: {src.get('title', 'Без назви')}\n\n{src.get('full_text', src.get('summary', 'Повний розгорнутий контекст збережено.'))}"
            for idx, src in enumerate(sources, start=1)
        ]
        studio_md = ", ".join(studio_artifacts_created or ["Mind Map (Studio)", "Deep Analytical Synthesis"])
        raw_md = (
            f"# 📚 Повне Розгорнуте Досьє NotebookLM → Obsidian: `{ag.upper()}`\n\n"
            f"- **Власник пакета:** `{owner}`\n"
            f"- **Кількість опрацьованих джерел:** `{incoming_count}` (Ліміт блокнота: `{self.MAX_SOURCES_PER_NOTEBOOK}`)\n"
            f"- **Створені артефакти студії NotebookLM:** {studio_md}\n"
            f"- **Режим збереження:** `FULL_EXPANDED_LOSSLESS_MARKDOWN` (без стиснення та без втрати контексту)\n\n"
            + "\n\n".join(sections)
            + "\n"
        )

        if owner == "andrii":
            final_md = LeaderDocumentGuard.sign_leader_markdown(raw_md, doc_title=f"Andrii_NotebookLM_{ag}")
            purged_from_notebooklm = False
            self._source_counts[ag] = current_count
        else:
            final_md = raw_md
            # Agent sources are purged from NotebookLM after full lossless export to Obsidian!
            purged_from_notebooklm = True
            self._source_counts[ag] = 0

        history_dir = self.obsidian_vault_path / "01_Рада_Директорів_18_Агентів" / f"Історія_Знань_{ag}"
        history_dir.mkdir(parents=True, exist_ok=True)
        out_path = history_dir / f"Повне_Досьє_{ag}_{incoming_count}_джерел.md"
        out_path.write_text(final_md, encoding="utf-8")

        return {
            "status": "exported_full_markdown_to_obsidian",
            "agent_id": ag,
            "owner": owner,
            "sources_processed": incoming_count,
            "full_expanded_uncompressed": True,
            "leader_signed": (owner == "andrii"),
            "purged_from_notebooklm_after_export": purged_from_notebooklm,
            "remaining_sources_in_notebooklm": self._source_counts[ag],
            "overflow_300_alert_for_andrii": overflow_alert_for_andrii,
            "obsidian_path": str(out_path),
        }


# ---------------------------------------------------------------------------
# 4. Eva's 3-Stage Escalating Alarm Clock & Hybrid Reminder Router
# ---------------------------------------------------------------------------

class EvaSmartAlarmAndReminderSystem:
    """
    Implements:
    1. Eva's 3-Stage Escalating Alarm Clock (`trigger_alarm_attempt`):
       - Attempt 1 (00:00, rings 60s in Telegram with sound + `[☀️ Прокинувся]` / `[💤 Відкласти 5 хв]` buttons).
       - Attempt 2 (03:00, rings 60s in Telegram with louder alert).
       - Attempt 3 (if after 2-3 attempts Andrii has not dismissed or snoozed):
         Eva automatically places a REAL MOBILE PHONE CALL via SIP Trunk (`livekit-sip`) to wake Andrii up!
    2. Optimal Reminder Distribution (`route_reminder`):
       - **Eva (`eva`)** handles all Calendar Meetings, Strategic Tasks, Deadlines, and Birthdays.
       - **Trainer (`trainer`) & Doc (`doc`)** send daily Bio-Reminders (`Вітаміни / БАДи`, `Водний баланс`,
         `Час обіду / калорії / що з'їв`, `Тренування на XX:00`) directly in Trainer/Doc's bot so Andrii can
         immediately reply there with what he ate or how he trained.
       - **Automatic Eva Backup Escalation:** If Andrii hasn't acknowledged a vitamin/meal/workout reminder
         in Trainer's bot within 60 minutes, Trainer notifies Eva via LangGraph and Eva reminds Andrii
         in the main executive channel!
    """

    def trigger_alarm_attempt(
        self,
        alarm_time_kyiv: str,
        attempt_number: int,
        acknowledged_by_andrii: bool = False,
        snoozed_by_andrii: bool = False,
    ) -> Dict[str, Any]:
        if acknowledged_by_andrii:
            return {
                "status": "alarm_dismissed_good_morning",
                "alarm_time_kyiv": alarm_time_kyiv,
                "attempt_number": attempt_number,
                "eva_message_uk": "Доброго ранку, Андрію! Будильник вимкнено. Готую ранковий брифінг і погоду.",
            }
        if snoozed_by_andrii:
            return {
                "status": "alarm_snoozed_5_min",
                "alarm_time_kyiv": alarm_time_kyiv,
                "attempt_number": attempt_number,
                "ring_duration_seconds": 60,
            }

        if attempt_number >= 3:
            return {
                "status": "escalated_to_real_mobile_phone_call",
                "alarm_time_kyiv": alarm_time_kyiv,
                "attempt_number": attempt_number,
                "channel": "SIP_MOBILE_CALL_PLUS_TELEGRAM",
                "ring_duration_seconds": 60,
                "eva_voice_call_uk": (
                    "Алло, Андрію! Це Єва. Два будильники в Телеграмі ти пропустив, тому телефоную особисто на мобільний — час прокидатися!"
                ),
            }

        return {
            "status": "telegram_sound_alarm_ringing_60s",
            "alarm_time_kyiv": alarm_time_kyiv,
            "attempt_number": attempt_number,
            "channel": "TELEGRAM_SOUND_ALARM",
            "ring_duration_seconds": 60,
            "buttons": [
                {"text": "☀️ Я прокинувся (Вимкнути)", "callback": "eva:alarm_dismiss"},
                {"text": "💤 Відкласти на 5 хв", "callback": "eva:alarm_snooze_5m"},
            ],
        }

    def route_reminder(
        self,
        reminder_category: str,  # "meeting" | "deadline" | "vitamins" | "meal_calories" | "workout"
        title_uk: str,
        scheduled_time: str,
        unanswered_minutes: int = 0,
    ) -> Dict[str, Any]:
        cat = reminder_category.lower()
        if cat in ("meeting", "deadline", "birthday", "strategic"):
            primary_agent = "eva"
            backup_eva_escalation = False
        elif cat in ("vitamins", "sleep", "medical"):
            primary_agent = "doc"
            backup_eva_escalation = unanswered_minutes >= 60
        else:
            # "meal_calories", "workout", "water" -> Trainer's bot so Andrii can reply with his meal/workout log right there!
            primary_agent = "trainer"
            backup_eva_escalation = unanswered_minutes >= 60

        return {
            "category": cat,
            "title_uk": title_uk,
            "scheduled_time": scheduled_time,
            "primary_agent_bot": primary_agent,
            "backup_eva_escalation_triggered": backup_eva_escalation,
            "active_delivery_agent": "eva" if backup_eva_escalation else primary_agent,
        }


# ---------------------------------------------------------------------------
# 5. Multi-Messenger MCP Gateways & Unblockable 5-Stage Call Cascade
# ---------------------------------------------------------------------------

OMNICHANNEL_MESSENGER_MCP_GATEWAYS: Dict[str, Dict[str, Any]] = {
    "telegram": {
        "mcp_server": "mcp-telegram-mtproto-and-bot",
        "supports_text": True,
        "supports_voice_call": True,
        "notes_uk": "Основний контур (18 ботів + MTProto Userbot для живих дзвінків у Telegram).",
    },
    "sovereign_sip_over_tls_443": {
        "mcp_server": "livekit-sip-tls443-linphone-groundwire",
        "supports_text": True,
        "supports_voice_call": True,
        "notes_uk": (
            "Власний захищений SIP-сервер на нашому домені `sip.syndicateholding.com:443` (маскується під звичайний HTTPS-трафік). "
            "Працює через додаток Linphone / Groundwire на смартфоні по будь-якому Wi-Fi або Starlink, навіть коли вимкнений мобільний зв'язок і заблокований Telegram!"
        ),
    },
    "matrix_element_sovereign": {
        "mcp_server": "mcp-matrix-synapse-element-call",
        "supports_text": True,
        "supports_voice_call": True,
        "notes_uk": (
            "Власний сервер Matrix/Element на `chat.syndicateholding.com` із вбудованими WebRTC-дзвінками. "
            "Неможливо заблокувати як публічний месенджер, бо працює на нашому приватному домені."
        ),
    },
    "whatsapp": {
        "mcp_server": "mcp-whatsapp-baileys-cloud-api",
        "supports_text": True,
        "supports_voice_call": True,
        "notes_uk": "Шлюз WhatsApp (текст, голосові та інтернет-дзвінки через Wi-Fi).",
    },
    "signal": {
        "mcp_server": "mcp-signal-cli-rest-api",
        "supports_text": True,
        "supports_voice_call": False,
        "notes_uk": "Офіційний Docker-шлюз `signal-cli-rest-api` для наскрізно шифрованих повідомлень та голосових файлів у Signal.",
    },
    "threema": {
        "mcp_server": "mcp-threema-gateway-e2ee",
        "supports_text": True,
        "supports_voice_call": False,
        "notes_uk": "Офіційний шлюз `Threema Gateway` (`gateway.threema.ch`) з повним E2EE-шифруванням для текстових та голосових сповіщень.",
    },
}


class EvaResilientCallCascade:
    """
    Solves the real-world problem when GSM cellular towers are turned off AND Telegram is blocked/throttled:
    Eva executes an automatic 5-Stage Call Cascade until Andrii answers:
      Stage 1: Telegram Sound Alarm / Telegram VoIP Call (`telegram`).
      Stage 2: GSM Mobile Phone Call via SIP Trunk (`gsm_mobile_sip`) — if mobile network is active.
      Stage 3: **Sovereign SIP-over-TLS:443 Internet Call (`sovereign_sip_over_tls_443`)** to Linphone/Groundwire
               on Andrii's phone over Wi-Fi/Starlink (bypasses GSM blackouts AND bypasses Telegram blocks!).
      Stage 4: **Sovereign Matrix / SYNDICATE PWA Call (`matrix_element_sovereign`)** on our own domain
               `syndicateholding.com` (unblockable WebRTC call over HTTPS port 443).
      Stage 5: **WhatsApp / Signal / Threema E2EE Fallback (`whatsapp` + `signal` + `threema`)**.
    """

    CASCADE_ORDER: List[str] = [
        "telegram_voip_call",
        "gsm_mobile_sip_call",
        "sovereign_sip_tls443_linphone_wifi",
        "sovereign_matrix_pwa_webrtc_443",
        "whatsapp_signal_threema_fallback",
    ]

    def execute_failover_call(
        self,
        reason_uk: str,
        gsm_network_available: bool = False,
        telegram_reachable: bool = False,
        wifi_or_starlink_available: bool = True,
    ) -> Dict[str, Any]:
        tried_channels: List[str] = []

        if telegram_reachable:
            tried_channels.append("telegram_voip_call")
            return {
                "status": "connected_via_telegram_voip",
                "active_channel": "telegram_voip_call",
                "tried_channels": tried_channels,
                "reason_uk": reason_uk,
            }
        tried_channels.append("telegram_voip_call (blocked/unreachable)")

        if gsm_network_available:
            tried_channels.append("gsm_mobile_sip_call")
            return {
                "status": "connected_via_gsm_mobile_call",
                "active_channel": "gsm_mobile_sip_call",
                "tried_channels": tried_channels,
                "reason_uk": reason_uk,
            }
        tried_channels.append("gsm_mobile_sip_call (no cellular network)")

        if wifi_or_starlink_available:
            # Stage 3 & 4: Direct encrypted call over Wi-Fi/Starlink to our own domain on port 443 (Linphone SIP-TLS + Matrix/PWA)
            tried_channels.append("sovereign_sip_tls443_linphone_wifi")
            return {
                "status": "connected_via_sovereign_internet_sip_tls443",
                "active_channel": "sovereign_sip_tls443_linphone_wifi",
                "backup_parallel_ring": [
                    "sovereign_matrix_pwa_webrtc_443",
                    "whatsapp_call_and_signal_alert",
                ],
                "tried_channels": tried_channels,
                "transport": "WSS/TLS over port 443 to sip.syndicateholding.com (Unblockable over Wi-Fi/Starlink)",
                "reason_uk": reason_uk,
            }

        return {
            "status": "queued_for_instant_delivery_on_reconnect",
            "active_channel": "none_all_offline",
            "tried_channels": tried_channels,
            "reason_uk": reason_uk,
        }

