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
    assert a["status"] == "stored" and a["domain"] == "doc"
    dup = store.ingest("копія.md", b"abc")
    assert dup == {"status": "duplicate", "existing_id": a["id"]}
    odd = store.ingest("скан.xyz", b"zzz")
    assert odd["status"] == "needs_parser"
    assert "fmt:xyz" in store.pending and store.pending["fmt:xyz"]["state"] == "awaiting_andrii"
    audio = store.ingest("лекція.mp3", b"mp3data")
    assert audio["status"] == "needs_engine"


def test_medical_goes_to_immutable_and_cannot_be_written_or_deleted(store: KodexStore) -> None:
    m = store.ingest("аналіз_крові.pdf", b"lab", sensitivity="medical")
    assert m["domain"] == "andrii_medical_vault"
    assert store.rewrite(m["id"], "x" * 64, "fix")["reason"] == "immutable_domain"
    assert store.move(m["id"], "doc")["reason"] == "immutable_domain"
    assert store.request_delete(m["id"])["reason"] == "immutable_domain"


def test_delete_is_two_step_and_only_andrii_confirms(store: KodexStore) -> None:
    r = store.ingest("старе.md", b"old", text="тренування")
    req = store.request_delete(r["id"])
    assert req["status"] == "awaiting_confirmation"
    assert store.confirm_delete(req["token"], by="eva")["reason"] == "only_andrii_confirms"
    assert store.records[r["id"]].status == "stored"
    done = store.confirm_delete(req["token"], by="andrii")
    assert done["status"] == "trashed"
    assert store.records[r["id"]].status == "trashed"


def test_trash_purged_after_retention(store: KodexStore) -> None:
    r = store.ingest("тимчасове.md", b"t")
    req = store.request_delete(r["id"])
    store.confirm_delete(req["token"], by="andrii")
    later = datetime.now() + timedelta(days=kodex.TRASH_RETENTION_DAYS + 1)
    assert store.purge_expired(later) == [r["id"]]
    assert r["id"] not in store.records


def test_internet_blocked_until_andrii_approves(store: KodexStore) -> None:
    req = store.request_download("https://example.com/book.pdf", "книга")["request"]
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="eva")["reason"] == "only_andrii_approves"
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="andrii")["status"] == "approved"
    assert store.download_allowed(req) is True


def test_rewrite_keeps_versions_and_move_checks_domain(store: KodexStore) -> None:
    r = store.ingest("план.md", b"v1", text="тренування")
    store.rewrite(r["id"], "f" * 64, "очистка тексту")
    assert len(store.records[r["id"]].versions) == 2
    assert store.move(r["id"], "nope")["reason"] == "unknown_domain"
    assert store.move(r["id"], "fin")["status"] == "moved"


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
