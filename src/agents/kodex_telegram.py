"""K.O.D.E.K.S. — обробники Telegram-бота: кожна кнопка викликає метод KodexStore.

Чиста логіка без мережі: `KodexBot.handle_update(update)` приймає dict оновлення Telegram і повертає
список `Reply` (що надіслати). Мережу (getUpdates, sendMessage, завантаження файлів) робить
`tools/kodex_bot.py`, а тут її немає — тому тести йдуть без інтернету.

Правила доступу (жорсткі):
- Порожній allowlist — відмова всім (default-deny). Allowlist — ID Андрія (`KODEX_TELEGRAM_ALLOWED_CHAT_IDS`).
- Чужим відправникам бот не відповідає взагалі.
- Кожна зміна (чи то редагування, чи видалення мічених файлів) — лише після «Дозволити» від Андрія
  (`confirm`); «Заборонити» — `reject`.
- Завантаження з посилання — лише після `approve_download`. Сам запит (`request_download`) нічого не качає.

Що ще не підключено (деплой): транскрибація, переклад, розпізнавання фото/HEIC, вивчення нових форматів
(парсер) — кнопки відповідають чесним повідомленням і нічого не змінюють.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Tuple

from src.agents import kodex_buttons as kb
from src.agents.kodex import DOMAINS, PROTECTED_LABEL, KodexStore, Record

ALLOWLIST_ENV = "KODEX_TELEGRAM_ALLOWED_CHAT_IDS"
OWNER_SENDER = "andrii"
LIST_LIMIT = 30
REPORT_WINDOW = timedelta(hours=24)
FULL_REPORT_SINCE = datetime(2000, 1, 1)
ENGINE_PENDING = ("Рушій ще не підключено: вибір і встановлення безкоштовної транскрибації чи перекладу "
                  "відбувається при деплої. Нічого не змінено.")
FILE_FETCH_PENDING = "Завантаження файлів з Telegram ще не підключено на цьому сервері. Нічого не збережено."


@dataclass
class Reply:
    chat_id: str
    text: str
    markup: Optional[Dict[str, Any]] = None


def parse_allowlist(raw: Optional[str]) -> FrozenSet[str]:
    """Порожнє або відсутнє значення — порожній allowlist (відмова всім)."""
    if not raw:
        return frozenset()
    return frozenset(item.strip() for item in raw.split(",") if item.strip())


def _safe_name(raw: Optional[str], fallback: str) -> str:
    # Ім'я з Telegram — недовірений вхід: без шляхів і керуючих символів.
    base = os.path.basename((raw or "").replace("\\", "/")).strip()
    base = "".join(ch for ch in base if ch.isprintable())
    return base or fallback


def describe_ingest(res: Dict[str, Any]) -> str:
    status = res.get("status")
    if status == "duplicate":
        return "Такий файл уже є в архіві. Повторно не збережено."
    if status == "rejected":
        return f"Відхилено: {res.get('reason', 'невідома причина')}."
    if status == "needs_parser":
        text = "Збережено, але формат ще не відомий. Запит на вивчення — у «🧩 Вивчити новий формат»."
    elif status == "needs_engine":
        text = "Збережено. Розпізнавання (транскрибація, конвертація) — при деплої."
    else:
        text = f"Збережено. База: {res.get('domain')}. Мітка: {'так' if res.get('protected') else 'ні'}."
    if res.get("warning"):
        text += f"\n⚠️ {res['warning']}"
    return text


def format_report(rep: Dict[str, Any], title: str) -> str:
    lines = [f"📊 {title}", f"з: {rep.get('since')}"]
    lines.append(f"завантажено: {rep.get('ingested', 0)}, змінено: {rep.get('rewritten', 0)}, "
                 f"переміщено: {rep.get('moved', 0)}, у кошик: {rep.get('trashed', 0)}, "
                 f"дублікатів пропущено: {rep.get('duplicates_skipped', 0)}")
    by_actor = rep.get("actions_by_actor") or {}
    if by_actor:
        lines.append("за виконавцями: " + ", ".join(f"{k} — {v}" for k, v in sorted(by_actor.items())))
    for key, label in (("agent_edits", "Редагування агентами"), ("agent_deletes", "Видалення агентами"),
                       ("agent_moves", "Переміщення агентами")):
        items = rep.get(key) or []
        if items:
            lines.append(f"{label}:")
            for e in items[:LIST_LIMIT]:
                extra = f" (дозвіл: {e['approved_by']})" if e.get("approved_by") else ""
                lines.append(f"  • {e.get('actor')}: {e.get('name')}{extra}")
    waiting = rep.get("awaiting_andrii") or {}
    if any(waiting.values()):
        lines.append("Чекають рішення Андрія: " + ", ".join(f"{k} — {v}" for k, v in waiting.items() if v))
    lines.append(f"файлів з міткою: {rep.get('protected_files', 0)}")
    return "\n".join(lines)


class KodexBot:
    def __init__(self, store: KodexStore, allowlist: Iterable[str],
                 fetch_file: Optional[Callable[[str], bytes]] = None,
                 clock: Callable[[], datetime] = datetime.now) -> None:
        self.store = store
        self.allowlist: FrozenSet[str] = frozenset(str(x) for x in allowlist)
        self.fetch_file = fetch_file
        self.clock = clock
        # chat_id → очікуваний вхід: {"await": "upload"|"edit"|"link", ...}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------ доступ
    def sender_for(self, chat_id: Any, user_id: Any) -> Optional[str]:
        """Лише Андрій: і чат, і відправник мають бути в allowlist. Порожній allowlist — відмова."""
        if not self.allowlist:
            return None
        if str(chat_id) not in self.allowlist or str(user_id) not in self.allowlist:
            return None
        return OWNER_SENDER

    # ------------------------------------------------------------ вхід
    def handle_update(self, update: Dict[str, Any]) -> List[Reply]:
        self.store.purge_expired(self.clock())
        if "callback_query" in update:
            replies = self._on_callback(update["callback_query"])
        elif "message" in update:
            replies = self._on_message(update["message"])
        else:
            replies = []
        self.store.save()
        return replies

    def _on_message(self, msg: Dict[str, Any]) -> List[Reply]:
        chat_id = str((msg.get("chat") or {}).get("id", ""))
        user_id = (msg.get("from") or {}).get("id", "")
        if self.sender_for(chat_id, user_id) is None:
            return []  # чужим не відповідаємо
        text = (msg.get("text") or "").strip()
        if text in ("/start", "/menu"):
            self.sessions.pop(chat_id, None)
            return [self._menu(chat_id, "Меню KODEX. Бот приватний: лише Андрій.")]
        if msg.get("document"):
            return self._on_document(chat_id, msg["document"])
        if text:
            return self._on_text(chat_id, text)
        return []

    def _on_callback(self, cq: Dict[str, Any]) -> List[Reply]:
        msg = cq.get("message") or {}
        chat_id = str((msg.get("chat") or {}).get("id", ""))
        user_id = (cq.get("from") or {}).get("id", "")
        if self.sender_for(chat_id, user_id) is None:
            return []
        parsed = kb.handle_callback(cq.get("data", ""), OWNER_SENDER)
        if parsed is None:
            return [Reply(chat_id, "Ця кнопка застаріла або невідома. Нічого не змінено.")]
        return self._dispatch(chat_id, parsed)

    def _on_text(self, chat_id: str, text: str) -> List[Reply]:
        session = self.sessions.get(chat_id)
        if not session or session.get("await") != "link":
            return [self._menu(chat_id, "Оберіть дію в меню.")]
        if not text.lower().startswith("https://") or " " in text:
            return [Reply(chat_id, "Потрібне посилання, що починається з https://. Спробуйте ще раз.")]
        self.sessions.pop(chat_id, None)
        res = self.store.request_download(text, reason="запит з Telegram", actor=OWNER_SENDER)
        return [Reply(chat_id,
                      "Запит створено. Нічого не завантажується, доки ви не дозволите.\n" + text,
                      kb.build_keyboard("approve_download", OWNER_SENDER, req=res["request"]))]

    def _on_document(self, chat_id: str, doc: Dict[str, Any]) -> List[Reply]:
        session = self.sessions.get(chat_id)
        if not session or session.get("await") not in ("upload", "edit"):
            return [self._menu(chat_id, "Спочатку оберіть «Завантажити файл» або «Перезаписати» в меню. "
                                        "Без цього файл не приймається.")]
        if self.fetch_file is None:
            self.sessions.pop(chat_id, None)
            return [Reply(chat_id, FILE_FETCH_PENDING)]
        data = self.fetch_file(doc["file_id"])
        self.sessions.pop(chat_id, None)
        name = _safe_name(doc.get("file_name"), f"telegram_{doc.get('file_unique_id', 'file')}")
        if session["await"] == "upload":
            res = self.store.ingest(name, data, origin="andrii_kodex", actor=OWNER_SENDER,
                                    protect=bool(session.get("protect")))
            return [Reply(chat_id, describe_ingest(res))]
        return [self._after_change(chat_id, self.store.rewrite(
            session["id"], data, reason="перезапис з Telegram", actor=OWNER_SENDER), name)]

    # ------------------------------------------------------------ обробка кнопок
    def _dispatch(self, chat_id: str, p: Dict[str, Any]) -> List[Reply]:
        action, arg, param = p["action"], p["arg"], p["param"]
        self.sessions.pop(chat_id, None)
        handler = getattr(self, f"_do_{action}", None)
        if handler is None:
            return [Reply(chat_id, "Ця дія ще не підключена. Нічого не змінено.")]
        return handler(chat_id, arg, param)

    def _do_upload(self, chat_id: str, arg: str, _param: Optional[str]) -> List[Reply]:
        protect = arg == "await_file_protected"
        self.sessions[chat_id] = {"await": "upload", "protect": protect}
        if protect:
            return [Reply(chat_id, "Надішліть файл як документ. Він отримає мітку andrii_protected.")]
        return [Reply(chat_id, "Надішліть файл як документ. Без мітки: KODEX і агенти зможуть його "
                               "редагувати, сортувати й видаляти (видалене — у кошик на 30 днів).")]

    def _do_download(self, chat_id: str, arg: str, param: Optional[str]) -> List[Reply]:
        if arg == "ask_url":
            self.sessions[chat_id] = {"await": "link"}
            return [Reply(chat_id, "Надішліть посилання https://… Нічого не завантажуватиметься без вашого дозволу.")]
        if arg == "approve":
            res = self.store.approve_download(param, OWNER_SENDER)
            if res.get("status") != "approved":
                return [self._not_found(chat_id)]
            return [Reply(chat_id, "Дозволено. Саме завантаження ще не підключено на цьому сервері (деплой).")]
        res = self.store.reject_download(param, OWNER_SENDER)
        if res.get("status") != "denied":
            return [self._not_found(chat_id)]
        return [Reply(chat_id, "Завантаження заборонено. Нічого не завантажено.")]

    def _do_change(self, chat_id: str, arg: str, param: Optional[str]) -> List[Reply]:
        if arg == "confirm":
            res = self.store.confirm(param, OWNER_SENDER)
            if res.get("status") == "trashed":
                return [Reply(chat_id, f"🗑 У кошику на {res.get('restore_until_days')} днів: {self._name(res)}")]
            if res.get("status") == "rewritten":
                return [Reply(chat_id, f"✏️ Зміну дозволено й виконано (версій: {res.get('versions')}).")]
            return [self._not_found(chat_id)]
        res = self.store.reject(param, OWNER_SENDER)
        if res.get("status") != "denied":
            return [self._not_found(chat_id)]
        return [Reply(chat_id, "❌ Зміну заборонено. Файл не змінено.")]

    def _do_format(self, chat_id: str, arg: str, param: Optional[str]) -> List[Reply]:
        if arg == "ask_ext":
            exts = [k[len("fmt:"):] for k, v in self.store.pending.items()
                    if k.startswith("fmt:") and v.get("state") == "awaiting_andrii"]
            if not exts:
                return [Reply(chat_id, "Немає форматів, що чекають рішення.")]
            rows = []
            for ext in sorted(exts):
                if kb.PARAM_RE.match(ext):
                    rows.append([{"text": f".{ext} — вивчити", "callback_data": f"fmt:yes:{ext}"},
                                 {"text": "❌", "callback_data": f"fmt:no:{ext}"}])
            if not rows:
                return [Reply(chat_id, "Формати з недопустимими розширеннями не можна вивчити.")]
            rows.append([{"text": "⬅️ Меню", "callback_data": "menu:main"}])
            return [Reply(chat_id, "Формати, що чекають рішення:", {"inline_keyboard": rows})]
        if arg == "approve":
            res = self.store.approve_format(param, OWNER_SENDER)
            if res.get("status") != "approved_to_learn":
                return [self._not_found(chat_id)]
            return [Reply(chat_id, f"Формат .{param} дозволено вивчити. Парсер підключається при деплої.")]
        res = self.store.deny_format(param, OWNER_SENDER)
        if res.get("status") != "denied":
            return [self._not_found(chat_id)]
        return [Reply(chat_id, f"Формат .{param} не вивчаємо.")]

    def _do_delete(self, chat_id: str, arg: str, param: Optional[str]) -> List[Reply]:
        if arg == "pick_item":
            return [self._pick(chat_id, "Оберіть файл для видалення:", "del:pick", self._live())]
        res = self.store.request_delete(param, actor=OWNER_SENDER)
        if res.get("status") == "not_found":
            return [self._not_found(chat_id)]
        if res.get("status") == "trashed":
            return [Reply(chat_id, f"🗑 У кошику на {res.get('restore_until_days')} днів.")]
        name = self.store.records[param].name
        return [Reply(chat_id, f"Файл «{name}» з міткою andrii_protected. Видалити можна лише з вашого дозволу:",
                      kb.build_keyboard("confirm_delete", OWNER_SENDER, token=res["token"]))]

    def _do_label(self, chat_id: str, arg: str, param: Optional[str]) -> List[Reply]:
        if arg == "pick_unlabeled":
            return [self._pick(chat_id, "Оберіть файл, який позначити міткою:", "lbl:on",
                               self._live(protected=False))]
        if arg == "pick_labeled":
            return [self._pick(chat_id, "Оберіть файл, з якого зняти мітку:", "lbl:off",
                               self._live(protected=True))]
        if arg == "cancel":
            return [Reply(chat_id, "Мітку залишено.")]
        if arg == "label":
            res = self.store.label(param, OWNER_SENDER)
            if res.get("status") != "protected":
                return [self._not_found(chat_id)]
            return [Reply(chat_id, f"🔒 Мітку andrii_protected поставлено: {self._name(res, param)}")]
        if arg == "ask_unlabel":
            rec = self._record(param)
            if rec is None:
                return [self._not_found(chat_id)]
            return [Reply(chat_id, f"Зняти мітку з «{rec.name}»? Після цього KODEX і агенти зможуть його "
                                   "редагувати й видаляти.",
                          kb.build_keyboard("confirm_label_removal", OWNER_SENDER, id=param))]
        res = self.store.unlabel(param, OWNER_SENDER)
        if res.get("status") != "unprotected":
            return [self._not_found(chat_id)]
        return [Reply(chat_id, f"🔓 Мітку знято: {self._name(res, param)}")]

    def _do_archive(self, chat_id: str, _arg: str, _param: Optional[str]) -> List[Reply]:
        lines = ["🗂 Структура архіву:"]
        for domain in DOMAINS:
            recs = [r for r in self._live() if r.domain == domain]
            if not recs:
                continue
            lines.append(f"\n📁 {domain} ({len(recs)})")
            for r in recs[:LIST_LIMIT]:
                lock = "🔒 " if PROTECTED_LABEL in r.labels else ""
                lines.append(f"  {lock}{r.name}")
        if len(lines) == 1:
            lines.append("Архів порожній.")
        return [Reply(chat_id, "\n".join(lines)[:4000], kb.build_keyboard("back", OWNER_SENDER))]

    def _do_route(self, chat_id: str, _arg: str, _param: Optional[str]) -> List[Reply]:
        counts = {d: 0 for d in DOMAINS}
        for r in self._live():
            counts[r.domain] = counts.get(r.domain, 0) + 1
        lines = ["🧭 Розподіл по базах:"] + [f"{d}: {n}" for d, n in counts.items()]
        return [Reply(chat_id, "\n".join(lines), kb.build_keyboard("back", OWNER_SENDER))]

    def _do_edit(self, chat_id: str, arg: str, param: Optional[str]) -> List[Reply]:
        if arg == "pick_item":
            return [self._pick(chat_id, "Оберіть файл для перезапису:", "edit:pick", self._live())]
        rec = self._record(param)
        if rec is None:
            return [self._not_found(chat_id)]
        self.sessions[chat_id] = {"await": "edit", "id": param}
        return [Reply(chat_id, f"Надішліть нову версію «{rec.name}» як документ. Для мічених файлів "
                               "зміна потребує вашого дозволу.")]

    def _do_transcribe(self, chat_id: str, _arg: str, _param: Optional[str]) -> List[Reply]:
        return [Reply(chat_id, ENGINE_PENDING)]

    def _do_translate(self, chat_id: str, _arg: str, _param: Optional[str]) -> List[Reply]:
        return [Reply(chat_id, ENGINE_PENDING)]

    def _do_report(self, chat_id: str, arg: str, _param: Optional[str]) -> List[Reply]:
        if arg == "eva":
            rep = self.store.report_for_eva(self.clock() - REPORT_WINDOW)
            return [Reply(chat_id, format_report(rep, "Звіт для Єви за 24 год"))]
        rep = self.store.report_for_eva(FULL_REPORT_SINCE)
        return [Reply(chat_id, format_report(rep, "Повний звіт"))]

    def _do_menu(self, chat_id: str, _arg: str, _param: Optional[str]) -> List[Reply]:
        return [self._menu(chat_id, "Меню KODEX.")]

    # ------------------------------------------------------------ допоміжні
    def _menu(self, chat_id: str, text: str) -> Reply:
        return Reply(chat_id, text, kb.build_keyboard("main", OWNER_SENDER))

    def _not_found(self, chat_id: str) -> Reply:
        return Reply(chat_id, "Запис або запит не знайдено (можливо, уже оброблено чи у кошику). Нічого не змінено.")

    def _live(self, protected: Optional[bool] = None) -> List[Record]:
        recs = [r for r in self.store.records.values() if r.status != "trashed"]
        if protected is not None:
            recs = [r for r in recs if (PROTECTED_LABEL in r.labels) == protected]
        return sorted(recs, key=lambda r: r.created_at, reverse=True)

    def _record(self, rec_id: Optional[str]) -> Optional[Record]:
        return self.store._live(rec_id) if rec_id else None

    def _name(self, res: Dict[str, Any], rec_id: Optional[str] = None) -> str:
        rid = res.get("id") or rec_id
        rec = self.store.records.get(rid) if rid else None
        return rec.name if rec else "файл"

    def _after_change(self, chat_id: str, res: Dict[str, Any], name: str) -> Reply:
        if res.get("status") == "awaiting_andrii_permission":
            return Reply(chat_id, f"Файл «{name}» з міткою. Дозволити перезапис?",
                         kb.build_keyboard("approve_change", OWNER_SENDER, token=res["token"]))
        if res.get("status") == "rewritten":
            return Reply(chat_id, f"✏️ Перезаписано: {name} (версій: {res.get('versions')}).")
        return Reply(chat_id, "Запис не знайдено. Нічого не змінено.")

    def _pick(self, chat_id: str, text: str, head: str, recs: List[Record]) -> Reply:
        if not recs:
            return Reply(chat_id, "Немає файлів для цієї дії.", kb.build_keyboard("back", OWNER_SENDER))
        shown = recs[:LIST_LIMIT]
        items: List[Tuple[str, str]] = [
            (r.id, ("🔒 " if PROTECTED_LABEL in r.labels else "") + r.name) for r in shown
        ]
        suffix = f"\nПоказано {len(shown)} з {len(recs)} (найновіші)." if len(recs) > LIST_LIMIT else ""
        return Reply(chat_id, text + suffix, kb.item_keyboard(head, items))
