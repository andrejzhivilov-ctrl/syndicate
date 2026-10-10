from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.agents import kodex
from src.agents.kodex import KodexStore, classify, FORMATS
from src.agents.kodex_buttons import build_keyboard, handle_callback


@pytest.fixture
def store(tmp_path: Path) -> KodexStore:
    return KodexStore(tmp_path / "kodex.json")


def test_ingest_dedup_and_format_routing(store: KodexStore) -> None:
    a = store.ingest("рецепт_омлет.md", b"abc", text="рецепт білок")
    assert a["status"] == "stored" and a["domain"] == "doc" and a["protected"] is False
    assert store.ingest("копія.md", b"abc") == {"status": "duplicate", "existing_id": a["id"]}
    odd = store.ingest("скан.xyz", b"zzz")
    assert odd["status"] == "needs_parser"
    assert store.pending["fmt:xyz"]["state"] == "awaiting_andrii"
    assert store.ingest("лекція.mp3", b"mp3data")["status"] == "needs_engine"


def test_andrii_personal_upload_is_auto_labeled_and_read_only(store: KodexStore) -> None:
    m = store.ingest("аналіз_крові.pdf", b"lab", origin="andrii")
    assert m["protected"] is True and "andrii_protected" in store.records[m["id"]].labels
    assert store.rewrite(m["id"], "x" * 64, "fix", actor="doc")["reason"] == "protected_label"
    assert store.rewrite(m["id"], "x" * 64, "fix", actor="andrii")["reason"] == "protected_label"
    assert store.move(m["id"], "doc", actor="eva")["reason"] == "protected_label"
    assert store.request_delete(m["id"], actor="doc")["reason"] == "protected_label"
    assert store.request_delete(m["id"], actor="kodex")["reason"] == "protected_label"


def test_protected_delete_only_via_andrii_confirmation(store: KodexStore) -> None:
    m = store.ingest("виписка.pdf", b"v", origin="andrii")
    req = store.request_delete(m["id"], actor="andrii")
    assert req["status"] == "awaiting_confirmation"
    assert store.confirm_delete(req["token"], by="eva")["reason"] == "only_andrii_confirms"
    assert store.confirm_delete(req["token"], by="andrii")["status"] == "trashed"


def test_only_andrii_can_label_and_unlabel(store: KodexStore) -> None:
    r = store.ingest("нотатка.md", b"n", text="ринок")
    assert store.label(r["id"], by="sam")["reason"] == "only_andrii_labels"
    assert store.label(r["id"], by="andrii")["status"] == "protected"
    assert store.rewrite(r["id"], "y" * 64, "x", actor="sam")["reason"] == "protected_label"
    assert store.unlabel(r["id"], by="sam")["reason"] == "only_andrii_unlabels"
    assert store.unlabel(r["id"], by="andrii")["status"] == "unprotected"
    assert store.rewrite(r["id"], "y" * 64, "x", actor="sam")["status"] == "rewritten"


def test_unlabeled_files_agents_edit_and_delete_directly_and_report_lists_them(store: KodexStore) -> None:
    since = datetime.now() - timedelta(minutes=1)
    r = store.ingest("робочий.md", b"w", text="ринок")
    assert store.rewrite(r["id"], "z" * 64, "очистка", actor="sam")["status"] == "rewritten"
    assert store.move(r["id"], "fin", actor="fin")["status"] == "moved"
    assert store.request_delete(r["id"], actor="sam")["status"] == "trashed"
    rep = store.report_for_eva(since)
    assert rep["to"] == "eva" and rep["rewritten"] == 1 and rep["moved"] == 1 and rep["trashed"] == 1
    assert [e["actor"] for e in rep["agent_edits"]] == ["sam", "fin"]
    assert rep["agent_deletes"][0]["actor"] == "sam"


def test_agent_delete_goes_to_trash_and_purges(store: KodexStore) -> None:
    r = store.ingest("тимчасове.md", b"t")
    assert store.request_delete(r["id"], actor="kodex")["status"] == "trashed"
    later = datetime.now() + timedelta(days=kodex.TRASH_RETENTION_DAYS + 1)
    assert store.purge_expired(later) == [r["id"]]
    assert r["id"] not in store.records


def test_trash_retention_matches_constant(store: KodexStore) -> None:
    assert kodex.TRASH_RETENTION_DAYS == 30


def test_internet_blocked_until_andrii_approves(store: KodexStore) -> None:
    req = store.request_download("https://example.com/book.pdf", "книга")["request"]
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="eva")["reason"] == "only_andrii_approves"
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="andrii")["status"] == "approved"
    assert store.download_allowed(req) is True


def test_rewrite_keeps_versions_and_move_checks_domain(store: KodexStore) -> None:
    r = store.ingest("план.md", b"v1", text="тренування")
    store.rewrite(r["id"], "f" * 64, "очистка тексту", actor="kodex")
    assert len(store.records[r["id"]].versions) == 2
    assert store.move(r["id"], "nope", actor="kodex")["reason"] == "unknown_domain"
    assert store.move(r["id"], "fin", actor="kodex")["status"] == "moved"


def test_report_for_eva_counts_actions(store: KodexStore) -> None:
    since = datetime.now() - timedelta(minutes=1)
    store.ingest("a.md", b"1", text="бюджет")
    store.ingest("a2.md", b"1")
    rep = store.report_for_eva(since)
    assert rep["to"] == "eva" and rep["ingested"] == 1 and rep["duplicates_skipped"] == 1


def test_state_survives_reload(tmp_path: Path) -> None:
    p = tmp_path / "k.json"
    s = KodexStore(p)
    r = s.ingest("з.md", b"q", text="ринок")
    s.save()
    again = KodexStore(p)
    assert again.records[r["id"]].domain == "sam"


def test_classify_default_is_shared() -> None:
    assert classify("нотатки.md") == "shared"
    assert set(FORMATS["pdf"]) >= {"status"}


def test_buttons_only_andrii_and_delete_needs_confirm() -> None:
    kb = build_keyboard("confirm_delete", "andrii")
    assert any(b["callback_data"] == "del:yes" for row in kb["inline_keyboard"] for b in row)
    assert handle_callback("del:yes", "eva") is None
    assert handle_callback("del:yes", "andrii")["action"] == "delete"
    assert handle_callback("unknown", "andrii") is None
    for row in build_keyboard("main", "andrii")["inline_keyboard"]:
        assert all(len(b["callback_data"]) <= 64 for b in row)
