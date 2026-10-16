"""
Telegram connector — the primary human channel (Andrii) and HITL control surface.

Bot token is stored in Vault at ``secret/data/syndicate/telegram`` (key ``bot_token``).
Supports HTML messages, documents, inline keyboards (for HITL approve/reject),
callback answers and webhook registration.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import structlog

from src.integrations.base import BaseConnector

logger = structlog.get_logger(__name__)


class TelegramConnector(BaseConnector):
    SERVICE_NAME = "telegram"

    def __init__(self, vault_client: Any = None, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(vault_client, config)
        self._token: Optional[str] = None

    async def _base(self) -> str:
        if self._token is None:
            self._token = await self._get_secret("bot_token")
        return f"https://api.telegram.org/bot{self._token}"

    @staticmethod
    def build_inline_keyboard(buttons: List[List[Tuple[str, str]]]) -> Dict[str, Any]:
        """buttons: rows of (text, callback_data). Returns reply_markup dict."""
        return {
            "inline_keyboard": [
                [{"text": text, "callback_data": data} for text, data in row]
                for row in buttons
            ]
        }

    async def send_message(
        self,
        chat_id: Any,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{await self._base()}/sendMessage"
        payload: Dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return await self._request("POST", url, json=payload)

    async def send_document(
        self, chat_id: Any, document_url: str, caption: str = ""
    ) -> Dict[str, Any]:
        url = f"{await self._base()}/sendDocument"
        payload = {"chat_id": chat_id, "document": document_url, "caption": caption}
        return await self._request("POST", url, json=payload)

    async def answer_callback_query(
        self, callback_query_id: str, text: str = "", show_alert: bool = False
    ) -> Dict[str, Any]:
        url = f"{await self._base()}/answerCallbackQuery"
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
        }
        return await self._request("POST", url, json=payload)

    async def set_webhook(self, webhook_url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{await self._base()}/setWebhook"
        payload: Dict[str, Any] = {"url": webhook_url}
        if secret_token:
            payload["secret_token"] = secret_token
        return await self._request("POST", url, json=payload)

    async def health_check(self) -> Dict[str, Any]:
        try:
            url = f"{await self._base()}/getMe"
            me = await self._request("GET", url)
            return {
                "service": self.SERVICE_NAME,
                "healthy": bool(me.get("ok")),
                "detail": me.get("result", {}).get("username"),
            }
        except Exception as exc:  # noqa: BLE001
            return {"service": self.SERVICE_NAME, "healthy": False, "detail": str(exc)}
