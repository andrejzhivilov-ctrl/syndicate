"""Voice notes in the director bots: hear the owner, answer by voice when spoken to.

Operator decisions 28.10:

* Speech-to-text goes to OpenAI first. Local Whisper on this server's CPU took
  66 s (large-v3-turbo) to 153 s (large-v3) for a 15 s note, so it is only the
  fallback when OpenAI is unavailable.
* Voice replies use Respeecher's Ukrainian model, and only when the owner spoke
  first. Without a Respeecher key the reply stays text: no placeholder audio.

Nothing here decides what an agent says: the transcript goes through the normal
chat/task path, and only the final reply text is voiced.
"""
from __future__ import annotations

import asyncio
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

from src.agent_chat import FEMININE
from src.model_registry import model_for

logger = structlog.get_logger(__name__)

OPENAI_STT_URL = "https://api.openai.com/v1/audio/transcriptions"
LOCAL_WHISPER_URL = "http://whisper:9000/asr"
RESPEECHER_UA = "https://api.respeecher.com/v1/public/tts/ua-rt"

VOICE_MAX_SECONDS = 300          # longer notes are refused, not silently cut
VOICE_MAX_BYTES = 20 * 1024 * 1024  # Telegram getFile limit for bots
TTS_MAX_CHARS = 1500             # cost cap: ~2.5 c per voiced reply at $2/60k chars
OPENAI_TIMEOUT_S = 60
LOCAL_TIMEOUT_S = 300
TTS_TIMEOUT_S = 60


async def transcribe(audio: bytes, keys: Dict[str, Any], *, transport: Any = None) -> Tuple[Optional[str], str]:
    """(text, provider). Text is None when every provider failed or heard nothing."""
    openai_key = keys.get("openai_api_key")
    if openai_key:
        try:
            async with httpx.AsyncClient(timeout=OPENAI_TIMEOUT_S, transport=transport) as client:
                response = await client.post(
                    OPENAI_STT_URL,
                    headers={"Authorization": f"Bearer {openai_key}"},
                    data={"model": model_for("OPENAI_TRANSCRIBE"), "language": "uk", "response_format": "json"},
                    files={"file": ("voice.ogg", audio, "audio/ogg")},
                )
            if response.status_code == 200:
                text = str(response.json().get("text") or "").strip()
                return (text or None), "openai"
            logger.warning("voice_stt_openai_failed", status=response.status_code)
        except Exception as exc:  # noqa: BLE001 - fall back to local Whisper
            logger.warning("voice_stt_openai_error", error_type=type(exc).__name__)
    try:
        async with httpx.AsyncClient(timeout=LOCAL_TIMEOUT_S, transport=transport) as client:
            response = await client.post(LOCAL_WHISPER_URL, params={"language": "uk"},
                                         files={"audio_file": ("voice.ogg", audio, "application/octet-stream")})
        if response.status_code == 200:
            text = str(response.json().get("text") or "").strip()
            return (text or None), "whisper_local"
        logger.warning("voice_stt_local_failed", status=response.status_code)
    except Exception as exc:  # noqa: BLE001
        logger.warning("voice_stt_local_error", error_type=type(exc).__name__)
    return None, "none"


#: Respeecher voice ids chosen by the operator (29.10). Ids, not display names:
#: "Олеся: медіа" is ``olesia-media`` in GET /voices.
AGENT_VOICES: Dict[str, str] = {
    "eva": "olesia-media",
    "kira": "mariia-audiobook",
    "sam": "yevhen-audiobook",
    "trainer": "ihoreo-conversation",
    "jack": "oleksandr-commercial",
}
DEFAULT_VOICE = "yevhen-commercial"


def voice_for(agent_id: str, voices: List[Dict[str, Any]]) -> Optional[str]:
    """The operator's voice for the agent; if Respeecher lacks it, a stable gender-matched one."""
    if not voices:
        return None
    chosen = AGENT_VOICES.get(agent_id, DEFAULT_VOICE)
    if any(str(v.get("id")) == chosen for v in voices):
        return chosen
    logger.warning("voice_tts_assigned_voice_missing", agent_id=agent_id, voice=chosen)
    wanted = "female" if agent_id in FEMININE else "male"
    pool = [v for v in voices if str(v.get("gender", "")).lower() == wanted] or voices
    pool = sorted(pool, key=lambda v: str(v.get("id")))
    index = int(hashlib.sha1(agent_id.encode("utf-8")).hexdigest(), 16) % len(pool)
    return str(pool[index].get("id"))


class RespeecherTTS:
    """Respeecher Space API, Ukrainian model. Returns WAV (16-bit PCM) or None."""

    def __init__(self, api_key: str, *, transport: Any = None) -> None:
        self._key = api_key
        self._transport = transport
        self._voices: Optional[List[Dict[str, Any]]] = None

    async def voices(self) -> List[Dict[str, Any]]:
        if self._voices is None:
            async with httpx.AsyncClient(timeout=20, transport=self._transport) as client:
                response = await client.get(f"{RESPEECHER_UA}/voices", headers={"X-API-Key": self._key})
            data = response.json() if response.status_code == 200 else []
            self._voices = [v for v in data if isinstance(v, dict) and v.get("id")] if isinstance(data, list) else []
        return self._voices

    async def synthesize(self, agent_id: str, text: str) -> Optional[bytes]:
        try:
            voice = voice_for(agent_id, await self.voices())
            if voice is None:
                logger.warning("voice_tts_no_voices")
                return None
            async with httpx.AsyncClient(timeout=TTS_TIMEOUT_S, transport=self._transport) as client:
                response = await client.post(f"{RESPEECHER_UA}/tts/bytes", headers={"X-API-Key": self._key},
                                             json={"transcript": text[:TTS_MAX_CHARS], "voice": {"id": voice}})
            if response.status_code != 200 or not response.content:
                logger.warning("voice_tts_failed", status=response.status_code)
                return None
            return response.content
        except Exception as exc:  # noqa: BLE001 - the text reply has already been sent
            logger.warning("voice_tts_error", error_type=type(exc).__name__)
            return None


async def wav_to_ogg_opus(wav: bytes) -> Optional[bytes]:
    """Telegram voice notes must be OGG/Opus; ffmpeg ships in the agent image."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", "pipe:0",
            "-c:a", "libopus", "-b:a", "32k", "-ac", "1", "-f", "ogg", "pipe:1",
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        out, _ = await asyncio.wait_for(proc.communicate(wav), timeout=60)
    except Exception as exc:  # noqa: BLE001
        logger.warning("voice_ogg_convert_error", error_type=type(exc).__name__)
        return None
    if proc.returncode != 0 or not out:
        logger.warning("voice_ogg_convert_failed", returncode=proc.returncode)
        return None
    return out


#: Replies are text by default (operator, 29.10); the owner asks for a voice answer
#: in words: "відповідай голосом", "скажи голосом", "озвуч", "voice on".
_VOICE_REQUEST = re.compile(
    r"(голосом|голосов\w*|озвуч|\bvoice\s*on\b|\bвойс\b)",
    re.IGNORECASE,
)


def wants_voice(text: str) -> bool:
    """True when the owner explicitly asked for a spoken answer in this message."""
    return bool(text) and bool(_VOICE_REQUEST.search(text))


#: How Respeecher's Ukrainian model should read English terms it otherwise mangles.
#: Keys are matched as whole words; longer phrases first so "Google Drive" wins over "Google".
PRONUNCIATION: Dict[str, str] = {
    "Google Drive": "Ґуґл Драйв",
    "Google": "Ґуґл",
    "Obsidian": "Обсідіан",
    "Telegram": "Телеграм",
    "YouTube": "Ютуб",
    "GitHub": "Ґітхаб",
    "OpenAI": "Оупен Ей Ай",
    "OpenRouter": "Оупен Раутер",
    "Respeecher": "Ріспічер",
    "Anthropic": "Антропік",
    "Claude": "Клод",
    "Gemini": "Джеміні",
    "Grok": "Ґрок",
    "Perplexity": "Перплексіті",
    "Antigravity": "Антіґревіті",
    "n8n": "ен-ейт-ен",
    "Bitcoin": "біткоїн",
    "Ethereum": "етеріум",
    "USDT": "ю-ес-ді-ті",
    "P2P": "пі-ту-пі",
    "Brent": "Брент",
    "API": "ей-пі-ай",
    "AI": "ей-ай",
    "PDF": "пі-ді-еф",
    "CI": "сі-ай",
    "PR": "пі-ар",
    "LLM": "ел-ел-ем",
    "MCP": "ем-сі-пі",
    "VPN": "ві-пі-ен",
    "OK": "окей",
}
_PRONUNCIATION_BY_KEY = {k.casefold(): v for k, v in PRONUNCIATION.items()}
# Built only from the fixed dictionary keys above (escaped), never from user input.
_PRONUNCIATION_RE = re.compile(
    r"(?<![\w-])(" + "|".join(re.escape(k) for k in sorted(PRONUNCIATION, key=len, reverse=True)) + r")(?![\w-])",
    re.IGNORECASE,
)


def pronounceable(text: str) -> str:
    """Spell English terms the way the Ukrainian voice should say them, whatever their case."""
    return _PRONUNCIATION_RE.sub(lambda m: _PRONUNCIATION_BY_KEY[m.group(1).casefold()], text)


def spoken_text(reply: str) -> str:
    """What gets voiced: the reply without the transcript echo, capped for cost."""
    text = pronounceable(reply.strip())
    if len(text) > TTS_MAX_CHARS:
        tail = "… Повний текст — у повідомленні вище."
        text = text[: TTS_MAX_CHARS - len(tail)].rsplit(" ", 1)[0] + tail
    return text
