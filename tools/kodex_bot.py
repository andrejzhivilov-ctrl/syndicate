"""Запуск приватного Telegram-бота KODEX (long polling). Лише мережевий шар; логіка — src/agents/kodex_telegram.py.

Потрібні змінні середовища (значення — лише на сервері, не в git):
    TELEGRAM_BOT_TOKEN_KODEX          токен окремого бота KODEX
    KODEX_TELEGRAM_ALLOWED_CHAT_IDS   ID Андрія (Telegram user id; для приватного чату це й chat id)
    KODEX_DATA_DIR                    каталог сховища (kodex.json і blobs/), поза git

Порожній allowlist або відсутній токен — запуск відмовляється (default-deny).

Запуск:  python tools/kodex_bot.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.kodex import KodexStore  # noqa: E402
from src.agents.kodex_telegram import ALLOWLIST_ENV, KodexBot, parse_allowlist  # noqa: E402

log = logging.getLogger("kodex_bot")
TOKEN_ENV = "TELEGRAM_BOT_TOKEN_KODEX"
DATA_ENV = "KODEX_DATA_DIR"
API = "https://api.telegram.org"


def _config() -> Dict[str, Any]:
    token = os.getenv(TOKEN_ENV, "").strip()
    data_dir = os.getenv(DATA_ENV, "").strip()
    allow = parse_allowlist(os.getenv(ALLOWLIST_ENV))
    problems = []
    if not token:
        problems.append(f"немає {TOKEN_ENV}")
    if not data_dir:
        problems.append(f"немає {DATA_ENV}")
    if not allow:
        problems.append(f"порожній {ALLOWLIST_ENV} (відмова всім)")
    if problems:
        raise SystemExit("KODEX-бот не запущено: " + "; ".join(problems))
    return {"token": token, "data_dir": Path(data_dir), "allow": allow}


def _api(token: str, method: str, **params: Any) -> Dict[str, Any]:
    resp = httpx.post(f"{API}/bot{token}/{method}", json=params, timeout=60)
    body: Dict[str, Any] = resp.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram {method}: {body.get('description', 'помилка')}")
    return body


def make_fetch_file(token: str):
    def fetch_file(file_id: str) -> bytes:
        info = _api(token, "getFile", file_id=file_id)["result"]
        resp = httpx.get(f"{API}/file/bot{token}/{info['file_path']}", timeout=120)
        resp.raise_for_status()
        return resp.content
    return fetch_file


def send(token: str, chat_id: str, text: str, markup: Optional[Dict[str, Any]]) -> None:
    payload: Dict[str, Any] = {"chat_id": chat_id, "text": text[:4096]}
    if markup:
        payload["reply_markup"] = markup
    _api(token, "sendMessage", **payload)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = _config()
    token = cfg["token"]
    data_dir: Path = cfg["data_dir"]
    store = KodexStore(data_dir / "kodex.json", data_dir / "blobs")
    bot = KodexBot(store, cfg["allow"], fetch_file=make_fetch_file(token))
    offset: Optional[int] = None
    log.info("KODEX-бот запущено; відповідає лише allowlist (%d шт.)", len(cfg["allow"]))
    while True:
        try:
            resp = httpx.get(f"{API}/bot{token}/getUpdates", timeout=70, params={
                "timeout": 50, "offset": offset, "allowed_updates": json.dumps(["message", "callback_query"]),
            })
            body = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            # Винятки httpx містять URL з токеном — у лог пишемо лише тип.
            log.error("getUpdates недоступний (%s); повтор через 5 с", type(exc).__name__)
            time.sleep(5)
            continue
        if not body.get("ok"):
            log.error("getUpdates: %s", body.get("description", "помилка"))
            time.sleep(5)
            continue
        for update in body.get("result", []):
            offset = update["update_id"] + 1
            try:
                for reply in bot.handle_update(update):
                    send(token, reply.chat_id, reply.text, reply.markup)
                if "callback_query" in update:
                    _api(token, "answerCallbackQuery", callback_query_id=update["callback_query"]["id"])
            except Exception as exc:  # noqa: BLE001 — один збійний апдейт не зупиняє бота
                # Лише тип помилки: текст може містити URL з токеном або вміст файлу.
                log.error("оновлення %s не оброблено (%s)", update.get("update_id"), type(exc).__name__)


if __name__ == "__main__":
    main()
