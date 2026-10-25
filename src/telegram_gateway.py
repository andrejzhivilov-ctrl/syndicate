"""Telegram gateway for the 18 director bots.

One HTTPS endpoint (``POST /webhook/telegram/{agent_id}``) serves all bots. The
gateway — not the agents — owns the Telegram credentials:

* each director has its own bot token in Vault (``secret/syndicate/telegram/<id>``);
* each bot's webhook carries its own secret, *derived* from the server webhook
  secret (``HMAC-SHA256(master, "telegram-webhook|<id>")``). Telegram sends it
  back in ``X-Telegram-Bot-Api-Secret-Token``, so a request meant for one bot
  cannot be replayed against another bot's route;
* only the owner's Telegram user id (Vault ``telegram.owner_user_id``) is
  served. Everyone else is dropped silently and never reaches an agent.

Nothing here invents a reply: if the agent returns no usable text the user is
told exactly that.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

import httpx
import structlog

from src.vault_paths import DIRECTOR_IDS

logger = structlog.get_logger(__name__)

TELEGRAM_API = "https://api.telegram.org"
MAX_TEXT = 3500
REPLY_KEYS = ("reply", "response", "text", "message", "answer", "summary", "briefing")


def is_director(agent_id: str) -> bool:
    return agent_id in DIRECTOR_IDS


def derive_webhook_secret(master_secret: str, agent_id: str) -> str:
    """Per-bot webhook secret. Hex, so it fits Telegram's [A-Za-z0-9_-] rule."""
    if not master_secret:
        raise ValueError("master webhook secret is required")
    if not is_director(agent_id):
        raise ValueError("unknown director")
    digest = hmac.new(
        master_secret.encode("utf-8"), f"telegram-webhook|{agent_id}".encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return digest


def verify_webhook_secret(master_secret: Optional[str], agent_id: str, presented: Optional[str]) -> bool:
    if not master_secret or not presented or not is_director(agent_id):
        return False
    expected = derive_webhook_secret(master_secret, agent_id)
    return hmac.compare_digest(expected.encode("utf-8"), presented.encode("utf-8"))


def extract_message(update: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Reduce a Telegram update to the few fields an agent may see."""
    if not isinstance(update, Mapping):
        return None
    message = update.get("message") or update.get("edited_message")
    callback = update.get("callback_query")
    if isinstance(callback, Mapping):
        sender = callback.get("from") or {}
        msg = callback.get("message") or {}
        chat = msg.get("chat") or {}
        data = callback.get("data")
        if sender.get("id") is None or chat.get("id") is None or not isinstance(data, str):
            return None
        return {
            "kind": "callback",
            "user_id": str(sender["id"]),
            "chat_id": str(chat["id"]),
            "chat_type": chat.get("type", ""),
            "text": data[:256],
        }
    if not isinstance(message, Mapping):
        return None
    sender = message.get("from") or {}
    chat = message.get("chat") or {}
    text = message.get("text")
    if sender.get("id") is None or chat.get("id") is None or not isinstance(text, str):
        return None
    return {
        "kind": "message",
        "user_id": str(sender["id"]),
        "chat_id": str(chat["id"]),
        "chat_type": chat.get("type", ""),
        "text": text[:4000],
        "message_id": message.get("message_id"),
    }


def reply_text(agent_id: str, outcome: Mapping[str, Any]) -> str:
    """Turn an orchestrator outcome into honest Telegram text."""
    result = outcome.get("result")
    status = str(outcome.get("status", ""))
    if isinstance(result, Mapping):
        if result.get("hitl_item_id") or result.get("required_hitl"):
            item = result.get("hitl_item_id") or "—"
            return f"⏸ [{agent_id}] Дію утримано до твого рішення (черга HITL: {item})."
        if str(result.get("status", "")).lower() == "unavailable":
            reason = result.get("reason") or result.get("warning") or "причину не вказано"
            return f"⚠️ [{agent_id}] недоступно: {reason}"
        if result.get("error") or str(result.get("status", "")).lower() in {"error", "failed", "denied"}:
            reason = result.get("error") or result.get("reason") or result.get("status")
            return f"⛔ [{agent_id}] не виконано: {reason}"
        for key in REPLY_KEYS:
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:MAX_TEXT]
        return f"[{agent_id}] статус: {status or 'ok'}\n" + json.dumps(
            result, ensure_ascii=False, default=str
        )[: MAX_TEXT - 40]
    if isinstance(result, str) and result.strip():
        return result.strip()[:MAX_TEXT]
    return f"[{agent_id}] агент не повернув тексту (статус: {status or 'невідомо'})."


class TelegramGateway:
    def __init__(self, vault: Any, *, owner_user_id: Optional[str] = None, transport: Any = None) -> None:
        self._vault = vault
        self._owner = owner_user_id
        self._transport = transport

    async def owner_user_id(self) -> Optional[str]:
        if self._owner:
            return str(self._owner)
        try:
            secret = await self._vault.get_secret("secret/data/syndicate/telegram")
        except Exception:  # noqa: BLE001 - treated as "no owner configured"
            return None
        value = (secret or {}).get("owner_user_id")
        return str(value) if value else None

    async def is_owner(self, user_id: str) -> bool:
        owner = await self.owner_user_id()
        return bool(owner) and hmac.compare_digest(owner.encode("utf-8"), str(user_id).encode("utf-8"))

    async def bot_token(self, agent_id: str) -> Optional[str]:
        if not is_director(agent_id):
            return None
        try:
            secret = await self._vault.get_secret(f"secret/data/syndicate/telegram/{agent_id}")
        except Exception:  # noqa: BLE001
            return None
        token = (secret or {}).get("bot_token")
        return token if isinstance(token, str) and token else None

    async def send(self, agent_id: str, chat_id: str, text: str) -> bool:
        token = await self.bot_token(agent_id)
        if not token:
            logger.warning("telegram_send_no_token", agent_id=agent_id)
            return False
        try:
            async with httpx.AsyncClient(timeout=15, transport=self._transport, follow_redirects=False) as client:
                response = await client.post(
                    f"{TELEGRAM_API}/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": text[:MAX_TEXT], "disable_web_page_preview": True},
                )
            if response.status_code != 200:
                logger.warning("telegram_send_failed", agent_id=agent_id, status=response.status_code)
                return False
            return True
        except Exception as exc:  # noqa: BLE001 - never log the URL: it contains the token
            logger.warning("telegram_send_error", agent_id=agent_id, error_type=type(exc).__name__)
            return False

    async def register_webhooks(
        self, base_url: str, master_secret: str, agents: Iterable[str] = DIRECTOR_IDS
    ) -> List[Dict[str, Any]]:
        """Point every configured bot at ``<base_url>/webhook/telegram/<id>``."""
        if not base_url.startswith("https://"):
            raise ValueError("Telegram requires an https:// webhook URL")
        report: List[Dict[str, Any]] = []
        for agent_id in agents:
            token = await self.bot_token(agent_id)
            if not token:
                report.append({"agent": agent_id, "status": "no_token"})
                continue
            body = {
                "url": f"{base_url.rstrip('/')}/webhook/telegram/{agent_id}",
                "secret_token": derive_webhook_secret(master_secret, agent_id),
                "allowed_updates": ["message", "callback_query"],
                "drop_pending_updates": True,
            }
            try:
                async with httpx.AsyncClient(timeout=15, transport=self._transport, follow_redirects=False) as client:
                    response = await client.post(f"{TELEGRAM_API}/bot{token}/setWebhook", json=body)
                ok = response.status_code == 200 and bool(response.json().get("ok"))
                report.append({"agent": agent_id, "status": "ok" if ok else f"http_{response.status_code}"})
            except Exception as exc:  # noqa: BLE001
                report.append({"agent": agent_id, "status": f"error:{type(exc).__name__}"})
        return report
