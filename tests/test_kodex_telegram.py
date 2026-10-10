"""Тести обробників Telegram-бота KODEX. Без мережі: fetch_file — заглушка, відповіді — dataclass Reply."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pytest

from src.agents import kodex, kodex_buttons as kb
from src.agents.kodex import KodexStore, sha256_of
from src.agents.kodex_telegram import ENGINE_PENDING, KodexBot, Reply, parse_allowlist

OWNER_ID = "111"
NOW = datetime(2026, 10, 10, 12, 0, 0)


class FakeFiles:
    def __init__(self) -> None:
        self.by_id: Dict[str, bytes] = {}

    def __call__(self, file_id: str) -> bytes:
        return self.by_id[file_id]


@pytest.fixture
def files() -> FakeFiles:
    return FakeFiles()


@pytest.fixture
def store(tmp_path: Path) -> KodexStore:
    return KodexStore(tmp_path / "kodex.json", tmp_path / "blobs")


@pytest.fixture
def bot(store: KodexStore, files: FakeFiles) -> KodexBot:
    return KodexBot(store, [OWNER_ID], fetch_file=files, clock=lambda: NOW)


def msg(text: str, chat: str = OWNER_ID, user: str = OWNER_ID) -> Dict[str, Any]:
    return {"message": {"chat": {"id": int(chat)}, "from": {"id": int(user)}, "text": text}}


def doc(file_id: str, name: str, chat: str = OWNER_ID, user: str = OWNER_ID) -> Dict[str, Any]:
    return {"message": {"chat": {"id": int(chat)}, "from": {"id": int(user)},
                        "document": {"file_id": file_id, "file_name": name, "file_unique_id": "u" + file_id}}}


def cb(data: str, chat: str = OWNER_ID, user: str = OWNER_ID) -> Dict[str, Any]:
    return {"callback_query": {"id": "q", "from": {"id": int(user)}, "data": data,
                               "message": {"chat": {"id": int(chat)}}}}


def callbacks(reply: Reply) -> List[str]:
    return [b["callback_data"] for row in (reply.markup or {}).get("inline_keyboard", []) for b in row]


def find_cb(reply: Reply, prefix: str) -> str:
    matches = [c for c in callbacks(reply) if c.startswith(prefix)]
    assert matches, (prefix, callbacks(reply))
    return matches[0]


def ingest(store: KodexStore, name: str, data: bytes, **kw: Any) -> str:
    return store.ingest(name, data, **kw)["id"]


# ---------------------------------------------------------------- доступ і default-deny

def test_parse_allowlist_empty_means_deny_all() -> None:
    assert parse_allowlist(None) == frozenset()
    assert parse_allowlist("") == frozenset()
    assert parse_allowlist(" 111 , 222 ") == frozenset({"111", "222"})


def test_empty_allowlist_denies_everything(store: KodexStore, files: FakeFiles) -> None:
    files.by_id["f1"] = b"x"
    bot = KodexBot(store, [], fetch_file=files, clock=lambda: NOW)
    assert bot.handle_update(msg("/start")) == []
    assert bot.handle_update(cb("rep:eva")) == []
    assert bot.handle_update(doc("f1", "a.md")) == []
    assert store.records == {}


def test_strangers_get_no_reply_and_change_nothing(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    files.by_id["f1"] = b"x"
    ingest(store, "робочий.md", b"w")
    bot.handle_update(cb("up:file", chat="999", user="999"))
    assert bot.handle_update(doc("f1", "чужий.md", chat="999", user="999")) == []
    assert bot.handle_update(cb("del:start", chat="999", user="999")) == []
    assert len(store.records) == 1


def test_chat_or_user_must_both_be_allowed(store: KodexStore) -> None:
    bot = KodexBot(store, [OWNER_ID])
    assert bot.handle_update(msg("/start", chat=OWNER_ID, user="999")) == []
    assert bot.handle_update(msg("/start", chat="999", user=OWNER_ID)) == []


def test_unrelated_update_is_ignored(bot: KodexBot) -> None:
    assert bot.handle_update({"edited_message": {"chat": {"id": 111}, "from": {"id": 111}}}) == []


def test_menu_offers_only_andrii_buttons_and_all_parse(bot: KodexBot) -> None:
    (reply,) = bot.handle_update(msg("/start"))
    for c in callbacks(reply):
        assert kb.handle_callback(c, "andrii") is not None, c
        assert kb.handle_callback(c, "eva") is None


# ---------------------------------------------------------------- завантаження

def test_upload_without_label_warns_and_stores(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    files.by_id["f1"] = b"plain text"
    (ask,) = bot.handle_update(cb("up:file"))
    assert "без мітки" in ask.text.lower()
    (reply,) = bot.handle_update(doc("f1", "виписка.md"))
    assert "⚠️" in reply.text and "Збережено" in reply.text
    (rec,) = store.records.values()
    assert rec.labels == [] and rec.origin == "andrii_kodex" and rec.name == "виписка.md"
    assert store.read_bytes(rec.id) == b"plain text"


def test_upload_protected_gets_label(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    files.by_id["f1"] = b"lab"
    bot.handle_update(cb("up:protected"))
    (reply,) = bot.handle_update(doc("f1", "аналіз.pdf"))
    assert "⚠️" not in reply.text
    (rec,) = store.records.values()
    assert kodex.PROTECTED_LABEL in rec.labels


def test_document_without_upload_session_is_refused(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    files.by_id["f1"] = b"x"
    (reply,) = bot.handle_update(doc("f1", "випадково.md"))
    assert "Спочатку" in reply.text
    assert store.records == {}


def test_upload_without_fetcher_stores_nothing(store: KodexStore) -> None:
    bot = KodexBot(store, [OWNER_ID], fetch_file=None, clock=lambda: NOW)
    bot.handle_update(cb("up:file"))
    (reply,) = bot.handle_update(doc("f1", "a.md"))
    assert "не підключено" in reply.text
    assert store.records == {}


def test_telegram_filename_is_sanitized(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    files.by_id["f1"] = b"x"
    bot.handle_update(cb("up:file"))
    bot.handle_update(doc("f1", "../../etc/passwd.md"))
    (rec,) = store.records.values()
    assert rec.name == "passwd.md"


# ---------------------------------------------------------------- посилання і дозвіл на інтернет

def test_link_request_needs_andrii_approval(bot: KodexBot, store: KodexStore) -> None:
    bot.handle_update(cb("up:link"))
    (reply,) = bot.handle_update(msg("https://example.com/book.pdf"))
    req_cb = find_cb(reply, "net:yes:")
    assert store.download_allowed(req_cb.split(":")[-1]) is False
    (done,) = bot.handle_update(cb(req_cb))
    assert "Дозволено" in done.text
    assert store.download_allowed(req_cb.split(":")[-1]) is True


def test_link_denied_stays_denied(bot: KodexBot, store: KodexStore) -> None:
    bot.handle_update(cb("up:link"))
    (reply,) = bot.handle_update(msg("https://example.com/x.pdf"))
    (done,) = bot.handle_update(cb(find_cb(reply, "net:no:")))
    assert "заборонено" in done.text
    assert all(v.get("state") != "approved" for k, v in store.pending.items() if k.startswith("net:"))


def test_link_must_be_https(bot: KodexBot) -> None:
    bot.handle_update(cb("up:link"))
    (reply,) = bot.handle_update(msg("ftp://example.com/x"))
    assert "https" in reply.text
    assert bot.sessions == {"111": {"await": "link"}}


def test_text_without_session_gets_menu(bot: KodexBot, store: KodexStore) -> None:
    (reply,) = bot.handle_update(msg("https://example.com/x.pdf"))
    assert "Оберіть дію" in reply.text
    assert store.pending == {}


def test_stale_download_approval_is_not_found(bot: KodexBot) -> None:
    (reply,) = bot.handle_update(cb("net:yes:deadbeef"))
    assert "не знайдено" in reply.text


# ---------------------------------------------------------------- видалення

def test_delete_unlabeled_goes_to_trash_at_once(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "тимчасове.md", b"t")
    (listing,) = bot.handle_update(cb("del:start"))
    assert find_cb(listing, f"del:pick:{rid}") == f"del:pick:{rid}"
    (reply,) = bot.handle_update(cb(f"del:pick:{rid}"))
    assert "кошику" in reply.text and store.records[rid].status == "trashed"
    assert store.read_bytes(rid) is None


def test_delete_labeled_needs_token_confirmation(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "аналіз.md", b"a", origin="andrii_direct")
    (ask,) = bot.handle_update(cb(f"del:pick:{rid}"))
    assert store.records[rid].status == "stored"
    yes = find_cb(ask, "chg:yes:")
    (done,) = bot.handle_update(cb(yes))
    assert "кошику" in done.text and store.records[rid].status == "trashed"


def test_delete_labeled_denied_keeps_file(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "аналіз.md", b"a", origin="andrii_direct")
    (ask,) = bot.handle_update(cb(f"del:pick:{rid}"))
    (done,) = bot.handle_update(cb(find_cb(ask, "chg:no:")))
    assert "заборонено" in done.text
    assert store.records[rid].status == "stored" and store.read_bytes(rid) == b"a"


def test_forged_or_reused_token_changes_nothing(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "аналіз.md", b"a", origin="andrii_direct")
    (ask,) = bot.handle_update(cb(f"del:pick:{rid}"))
    yes = find_cb(ask, "chg:yes:")
    (forged,) = bot.handle_update(cb("chg:yes:00000000"))
    assert "не знайдено" in forged.text and store.records[rid].status == "stored"
    bot.handle_update(cb(yes))
    (again,) = bot.handle_update(cb(yes))
    assert "не знайдено" in again.text


def test_agent_delete_approved_by_andrii_shows_in_report(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "аналіз.md", b"a", origin="andrii_direct")
    req = store.request_delete(rid, actor="sam")
    (done,) = bot.handle_update(cb(f"chg:yes:{req['token']}"))
    assert "кошику" in done.text
    (rep,) = bot.handle_update(cb("rep:full"))
    assert "Видалення агентами" in rep.text
    assert "sam" in rep.text and "дозвіл: andrii" in rep.text


def test_delete_pick_unknown_id_is_not_found(bot: KodexBot) -> None:
    (reply,) = bot.handle_update(cb("del:pick:abcdef012345"))
    assert "не знайдено" in reply.text


# ---------------------------------------------------------------- редагування

def test_edit_unlabeled_applies_new_bytes(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    rid = ingest(store, "нотатка.md", b"old")
    files.by_id["new"] = b"new text"
    (listing,) = bot.handle_update(cb("edit:start"))
    bot.handle_update(cb(f"edit:pick:{rid}"))
    (done,) = bot.handle_update(doc("new", "нотатка.md"))
    assert "Перезаписано" in done.text
    assert store.read_bytes(rid) == b"new text"


def test_edit_labeled_needs_andrii_approval(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    rid = ingest(store, "аналіз.md", b"old", origin="andrii_direct")
    files.by_id["new"] = b"changed"
    bot.handle_update(cb(f"edit:pick:{rid}"))
    (ask,) = bot.handle_update(doc("new", "аналіз.md"))
    assert store.read_bytes(rid) == b"old"
    (done,) = bot.handle_update(cb(find_cb(ask, "chg:yes:")))
    assert "виконано" in done.text or "Зміну дозволено" in done.text
    assert store.read_bytes(rid) == b"changed"


def test_edit_denied_keeps_old_bytes_and_removes_new(bot: KodexBot, store: KodexStore, files: FakeFiles) -> None:
    rid = ingest(store, "аналіз.md", b"old", origin="andrii_direct")
    files.by_id["new"] = b"secret-new"
    bot.handle_update(cb(f"edit:pick:{rid}"))
    (ask,) = bot.handle_update(doc("new", "аналіз.md"))
    bot.handle_update(cb(find_cb(ask, "chg:no:")))
    assert store.read_bytes(rid) == b"old"
    assert not store._blob_path(sha256_of(b"secret-new"), "md").exists()


def test_edit_pick_unknown_id_refuses_session(bot: KodexBot) -> None:
    (reply,) = bot.handle_update(cb("edit:pick:abcdef012345"))
    assert "не знайдено" in reply.text
    assert bot.sessions == {}


# ---------------------------------------------------------------- мітка

def test_label_on_and_off_round_trip(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "нотатка.md", b"n")
    (picker,) = bot.handle_update(cb("lbl:start"))
    assert find_cb(picker, f"lbl:on:{rid}")
    bot.handle_update(cb(f"lbl:on:{rid}"))
    assert kodex.PROTECTED_LABEL in store.records[rid].labels

    (offpick,) = bot.handle_update(cb("lbl:offstart"))
    assert find_cb(offpick, f"lbl:off:{rid}")
    (ask,) = bot.handle_update(cb(f"lbl:off:{rid}"))
    assert kodex.PROTECTED_LABEL in store.records[rid].labels  # ще не знято

    bot.handle_update(cb("lbl:offno"))
    assert kodex.PROTECTED_LABEL in store.records[rid].labels

    bot.handle_update(cb(f"lbl:offyes:{rid}"))
    assert kodex.PROTECTED_LABEL not in store.records[rid].labels


def test_label_removal_requires_andrii_menu_callback(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "нотатка.md", b"n")
    (reply,) = bot.handle_update(cb(f"lbl:off:{rid}"))
    assert "Зняти мітку" in reply.text
    assert kodex.PROTECTED_LABEL not in store.records[rid].labels


# ---------------------------------------------------------------- структура, розподіл, звіти

def test_tree_and_route_show_live_files_only(bot: KodexBot, store: KodexStore) -> None:
    ingest(store, "тренування.md", b"t", text="тренування")
    gone = ingest(store, "ринок.md", b"r", text="ринок")
    store.request_delete(gone, actor="kodex")
    (tree,) = bot.handle_update(cb("tree:show"))
    assert "тренування.md" in tree.text and "ринок.md" not in tree.text
    (route,) = bot.handle_update(cb("route:show"))
    assert "doc: 1" in route.text and "sam: 0" in route.text


def test_report_eva_has_window_and_agent_actions(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "робочий.md", b"w", origin="andrii_kodex")
    store.rewrite(rid, b"zzz", "очистка", actor="sam")
    (rep,) = bot.handle_update(cb("rep:eva"))
    assert "Звіт для Єви" in rep.text and "Редагування агентами" in rep.text and "sam" in rep.text


def test_full_report_lists_pending_permissions(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "аналіз.md", b"a", origin="andrii_direct")
    store.request_delete(rid, actor="kodex")
    (rep,) = bot.handle_update(cb("rep:full"))
    assert "Чекають рішення Андрія" in rep.text and "permission" in rep.text


def test_long_pick_list_is_capped(bot: KodexBot, store: KodexStore) -> None:
    for i in range(35):
        ingest(store, f"файл{i}.md", f"v{i}".encode())
    (reply,) = bot.handle_update(cb("del:start"))
    assert "Показано 30 з 35" in reply.text
    assert len(callbacks(reply)) == 31  # 30 записів + «Меню»


# ---------------------------------------------------------------- формати і рушії

def test_format_learning_approve_and_deny(bot: KodexBot, store: KodexStore) -> None:
    store.ingest("скан.xyz", b"zzz")
    store.ingest("інший.qqq", b"qqq")
    (listing,) = bot.handle_update(cb("fmt:learn"))
    assert find_cb(listing, "fmt:yes:xyz") and find_cb(listing, "fmt:no:qqq")
    (ok,) = bot.handle_update(cb("fmt:yes:xyz"))
    assert "дозволено вивчити" in ok.text
    assert store.pending["fmt:xyz"]["state"] == "approved_to_learn"
    (no,) = bot.handle_update(cb("fmt:no:qqq"))
    assert "не вивчаємо" in no.text and "fmt:qqq" not in store.pending


def test_format_learn_with_nothing_pending(bot: KodexBot) -> None:
    (reply,) = bot.handle_update(cb("fmt:learn"))
    assert "Немає форматів" in reply.text


@pytest.mark.parametrize("data", ["tr:start", "tl:start"])
def test_engine_actions_say_not_connected_and_change_nothing(bot: KodexBot, store: KodexStore, data: str) -> None:
    rid = ingest(store, "лекція.mp3", b"m")
    (reply,) = bot.handle_update(cb(data))
    assert reply.text == ENGINE_PENDING
    assert store.records[rid].status == "needs_engine"


# ---------------------------------------------------------------- меню, сесії, невідомі кнопки

def test_unknown_callback_changes_nothing(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "робочий.md", b"w")
    (reply,) = bot.handle_update(cb("drop:table"))
    assert "застаріла" in reply.text
    assert store.records[rid].status == "stored"


def test_bare_confirm_callback_is_rejected_by_bot(bot: KodexBot, store: KodexStore) -> None:
    rid = ingest(store, "аналіз.md", b"a", origin="andrii_direct")
    store.request_delete(rid, actor="kodex")
    (reply,) = bot.handle_update(cb("chg:yes"))
    assert "застаріла" in reply.text
    assert store.records[rid].status == "stored"


def test_menu_button_clears_pending_session(bot: KodexBot) -> None:
    bot.handle_update(cb("up:link"))
    assert bot.sessions
    (reply,) = bot.handle_update(cb("menu:main"))
    assert bot.sessions == {} and "Меню" in reply.text


def test_state_is_saved_after_each_update(bot: KodexBot, store: KodexStore, tmp_path: Path) -> None:
    rid = ingest(store, "нотатка.md", b"n")
    bot.handle_update(cb(f"lbl:on:{rid}"))
    reloaded = KodexStore(tmp_path / "kodex.json", tmp_path / "blobs")
    assert kodex.PROTECTED_LABEL in reloaded.records[rid].labels


def test_trash_is_purged_on_next_update_after_30_days(store: KodexStore) -> None:
    rid = ingest(store, "тимчасове.md", b"t")
    store.request_delete(rid, actor="kodex")
    later = NOW + timedelta(days=kodex.TRASH_RETENTION_DAYS + 1)
    bot = KodexBot(store, [OWNER_ID], clock=lambda: later)
    bot.handle_update(msg("/start"))
    assert rid not in store.records


# ---------------------------------------------------------------- покриття: кожна дія має обробник

def test_every_callback_action_has_a_handler() -> None:
    actions = {a for a, _ in kb.ACTIONS.values()} | {a for a, _ in kb.PARAM_ACTIONS.values()}
    for action in actions:
        assert hasattr(KodexBot, f"_do_{action}"), f"немає обробника _do_{action}"


def test_every_menu_button_parses_to_a_known_action() -> None:
    for menu, rows in kb.MENUS.items():
        for row in rows:
            for _text, template, _who in row:
                probe = template.format(token="abcd1234", req="abcd1234", id="abcdef012345", ext="xyz")
                parsed = kb.handle_callback(probe, "andrii")
                assert parsed is not None, (menu, probe)
                assert hasattr(KodexBot, f"_do_{parsed['action']}"), (menu, probe)


def test_every_static_action_has_a_test_case() -> None:
    # Нові статичні дії мають з'явитися тут (і в тестах вище), щоб не лишилися без покриття.
    assert set(kb.ACTIONS) == {
        "up:file", "up:protected", "up:link", "lbl:start", "lbl:offstart", "lbl:offno", "tree:show",
        "edit:start", "del:start", "route:show", "tr:start", "tl:start", "fmt:learn", "rep:eva", "rep:full",
        "menu:main",
    }
