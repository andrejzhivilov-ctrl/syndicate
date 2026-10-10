from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.agents import kodex
from src.agents.kodex import FORMATS, UNPROTECTED_WARNING, KodexStore, classify, sha256_of


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


def test_direct_personal_upload_is_auto_labeled(store: KodexStore) -> None:
    m = store.ingest("аналіз_крові.pdf", b"lab", origin="andrii_direct")
    assert m["protected"] is True and "andrii_protected" in store.records[m["id"]].labels
    assert "warning" not in m


def test_kodex_upload_without_label_warns_immediately(store: KodexStore) -> None:
    u = store.ingest("виписка.pdf", b"v", origin="andrii_kodex")
    assert u["protected"] is False and u["warning"] == UNPROTECTED_WARNING
    assert store.records[u["id"]].labels == []


def test_kodex_upload_with_label_request_is_protected_without_warning(store: KodexStore) -> None:
    u = store.ingest("аналіз.pdf", b"a", origin="andrii_kodex", protect=True)
    assert u["protected"] is True and "warning" not in u


def test_unknown_origin_rejected(store: KodexStore) -> None:
    assert store.ingest("x.md", b"x", origin="stranger")["reason"] == "unknown_origin"


def test_unlabeled_files_all_manipulations_direct_and_reported(store: KodexStore) -> None:
    since = datetime.now() - timedelta(minutes=1)
    u = store.ingest("робочий.md", b"w", origin="andrii_kodex", text="ринок")
    assert store.rewrite(u["id"], b"zzz", "очистка", actor="sam")["status"] == "rewritten"
    assert store.move(u["id"], "fin", actor="fin")["status"] == "moved"
    assert store.request_delete(u["id"], actor="sam")["status"] == "trashed"
    rep = store.report_for_eva(since)
    assert rep["to"] == "eva" and rep["rewritten"] == 1 and rep["moved"] == 1 and rep["trashed"] == 1
    assert [e["actor"] for e in rep["agent_edits"]] == ["sam"]
    assert rep["agent_deletes"][0]["actor"] == "sam"
    assert rep["agent_moves"][0]["actor"] == "fin"


def test_protected_files_can_be_moved_by_agents_for_sorting(store: KodexStore) -> None:
    m = store.ingest("виписка.pdf", b"v", origin="andrii_direct")
    assert store.move(m["id"], "doc", actor="kodex")["status"] == "moved"
    rep = store.report_for_eva(datetime.now() - timedelta(minutes=1))
    assert rep["agent_moves"][0]["protected"] is True


def test_protected_edit_and_delete_need_andrii_permission(store: KodexStore) -> None:
    m = store.ingest("аналіз.pdf", b"a", origin="andrii_direct")
    req = store.rewrite(m["id"], b"qqq", "виправити", actor="doc")
    assert req["status"] == "awaiting_andrii_permission" and req["change"] == "rewrite"
    assert store.records[m["id"]].sha256 != sha256_of(b"qqq")
    assert store.confirm(req["token"], by="doc")["reason"] == "only_andrii_confirms"
    assert store.confirm(req["token"], by="andrii")["status"] == "rewritten"
    assert store.records[m["id"]].sha256 == sha256_of(b"qqq")
    dele = store.request_delete(m["id"], actor="kodex")
    assert dele["status"] == "awaiting_andrii_permission" and dele["change"] == "delete"
    assert store.records[m["id"]].status == "stored"
    assert store.confirm(dele["token"], by="andrii")["status"] == "trashed"


def test_andrii_can_deny_protected_change(store: KodexStore) -> None:
    m = store.ingest("аналіз.pdf", b"a", origin="andrii_direct")
    req = store.request_delete(m["id"], actor="kodex")
    assert store.reject(req["token"], by="kodex")["reason"] == "only_andrii_rejects"
    assert store.reject(req["token"], by="andrii")["status"] == "denied"
    assert store.records[m["id"]].status == "stored"


def test_only_andrii_can_label_and_unlabel(store: KodexStore) -> None:
    r = store.ingest("нотатка.md", b"n", text="ринок")
    assert store.label(r["id"], by="sam")["reason"] == "only_andrii_labels"
    assert store.label(r["id"], by="andrii")["status"] == "protected"
    assert store.unlabel(r["id"], by="sam")["reason"] == "only_andrii_unlabels"
    assert store.unlabel(r["id"], by="andrii")["status"] == "unprotected"
    assert store.rewrite(r["id"], b"yyy", "x", actor="sam")["status"] == "rewritten"


def test_agent_delete_goes_to_trash_and_purges(store: KodexStore) -> None:
    r = store.ingest("тимчасове.md", b"t")
    assert store.request_delete(r["id"], actor="kodex")["status"] == "trashed"
    later = datetime.now() + timedelta(days=kodex.TRASH_RETENTION_DAYS + 1)
    assert store.purge_expired(later) == [r["id"]]
    assert r["id"] not in store.records


def test_trash_retention_is_30_days() -> None:
    assert kodex.TRASH_RETENTION_DAYS == 30


def test_rewrite_keeps_versions_and_move_checks_domain(store: KodexStore) -> None:
    r = store.ingest("план.md", b"v1", text="тренування")
    store.rewrite(r["id"], b"fff", "очистка тексту", actor="kodex")
    assert len(store.records[r["id"]].versions) == 2
    assert store.move(r["id"], "nope", actor="kodex")["reason"] == "unknown_domain"
    assert store.move(r["id"], "fin", actor="kodex")["status"] == "moved"


def test_internet_blocked_until_andrii_approves(store: KodexStore) -> None:
    req = store.request_download("https://example.com/book.pdf", "книга")["request"]
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="eva")["reason"] == "only_andrii_approves"
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="andrii")["status"] == "approved"
    assert store.download_allowed(req) is True


def test_state_survives_reload(tmp_path: Path) -> None:
    p = tmp_path / "k.json"
    s = KodexStore(p)
    r = s.ingest("з.md", b"q", text="ринок")
    s.save()
    assert KodexStore(p).records[r["id"]].domain == "sam"


def test_classify_default_is_shared() -> None:
    assert classify("нотатки.md") == "shared"
    assert FORMATS["pdf"]["status"] == "vendored_parser"


def test_report_counts_pending_permissions(store: KodexStore) -> None:
    m = store.ingest("аналіз.pdf", b"a", origin="andrii_direct")
    store.request_delete(m["id"], actor="kodex")
    rep = store.report_for_eva(datetime.now() - timedelta(minutes=1))
    assert rep["awaiting_andrii"]["permission"] == 1 and rep["protected_files"] == 1


def test_buttons_only_andrii_and_changes_need_confirm() -> None:
    from src.agents.kodex_buttons import build_keyboard, handle_callback

    kb = build_keyboard("approve_change", "andrii", token="abcd1234")
    assert any(b["callback_data"] == "chg:yes:abcd1234" for row in kb["inline_keyboard"] for b in row)
    assert handle_callback("chg:yes:abcd1234", "eva") is None
    assert handle_callback("chg:yes:abcd1234", "andrii")["action"] == "change"
    assert handle_callback("unknown", "andrii") is None
    for row in build_keyboard("main", "andrii")["inline_keyboard"]:
        assert all(len(b["callback_data"]) <= 64 for b in row)


def test_bare_change_callbacks_without_token_are_rejected() -> None:
    # Голий «chg:yes» не знає, на яку зміну він відповідає — відхиляється.
    from src.agents.kodex_buttons import handle_callback

    assert handle_callback("chg:yes", "andrii") is None
    assert handle_callback("chg:no", "andrii") is None
    assert handle_callback("net:yes", "andrii") is None
    assert handle_callback("fmt:yes", "andrii") is None
    assert handle_callback("chg:yes:ZZZ!", "andrii") is None  # недопустимі символи параметра


def test_agent_delete_approved_by_andrii_is_still_in_report(store: KodexStore) -> None:
    # Регресія: агентське видалення мічених файлів, яке схвалив Андрій, мало зникати зі звіту Єві.
    m = store.ingest("аналіз.pdf", b"a", origin="andrii_direct")
    req = store.request_delete(m["id"], actor="kodex")
    store.confirm(req["token"], by="andrii")
    rep = store.report_for_eva(datetime.now() - timedelta(minutes=1))
    assert rep["agent_deletes"][0]["actor"] == "kodex"
    assert rep["agent_deletes"][0]["approved_by"] == "andrii"


def test_agent_rewrite_approved_by_andrii_is_in_report(store: KodexStore) -> None:
    m = store.ingest("план.pdf", b"a", origin="andrii_direct")
    req = store.rewrite(m["id"], b"b", "очистка", actor="doc")
    store.confirm(req["token"], by="andrii")
    rep = store.report_for_eva(datetime.now() - timedelta(minutes=1))
    assert rep["agent_edits"][0]["actor"] == "doc"
    assert rep["agent_edits"][0]["approved_by"] == "andrii"


def test_andrii_own_actions_are_not_in_agent_report(store: KodexStore) -> None:
    m = store.ingest("мій.md", b"a", origin="andrii_kodex", actor="andrii")
    store.rewrite(m["id"], b"b", "сам", actor="andrii")
    store.request_delete(m["id"], actor="andrii")
    rep = store.report_for_eva(datetime.now() - timedelta(minutes=1))
    assert rep["agent_edits"] == [] and rep["agent_deletes"] == []


def test_denied_protected_rewrite_removes_its_bytes(store: KodexStore) -> None:
    m = store.ingest("аналіз.md", b"old", origin="andrii_direct")
    req = store.rewrite(m["id"], "секретна нова версія".encode("utf-8"), "правка", actor="doc")
    path = store._blob_path(sha256_of("секретна нова версія".encode("utf-8")), "md")
    assert path.exists()
    assert store.reject(req["token"], by="andrii")["status"] == "denied"
    assert not path.exists()
    assert store.read_bytes(m["id"]) == b"old"


def test_pending_counts_have_no_dead_keys(store: KodexStore) -> None:
    m = store.ingest("аналіз.pdf", b"a", origin="andrii_direct")
    store.request_delete(m["id"], actor="kodex")
    store.request_download("https://example.com/x.pdf", "книга")
    counts = store._pending_counts()
    assert counts == {"download": 1, "format": 0, "permission": 1}


def test_save_is_atomic_and_leaves_no_tmp(tmp_path: Path) -> None:
    s = KodexStore(tmp_path / "k.json")
    s.ingest("з.md", b"q")
    s.save()
    assert (tmp_path / "k.json").exists()
    assert not (tmp_path / "k.json.tmp").exists()


def test_reject_download_and_deny_format(store: KodexStore) -> None:
    req = store.request_download("https://example.com/b.pdf", "книга")["request"]
    assert store.reject_download(req, by="kodex")["reason"] == "only_andrii_approves"
    assert store.reject_download(req, by="andrii")["status"] == "denied"
    assert store.download_allowed(req) is False
    assert store.approve_download(req, by="andrii")["status"] == "not_found"
    store.ingest("скан.xyz", b"zzz")
    assert store.deny_format("xyz", by="andrii")["status"] == "denied"
    assert "fmt:xyz" not in store.pending


def test_photo_and_audio_are_stored_as_files_and_readable(store: KodexStore) -> None:
    photo = store.ingest("IMG_0412.HEIC", b"\x00heic-bytes", origin="andrii_kodex")
    assert photo["status"] == "needs_engine"  # HEIC потребує конвертації при деплої, але байти збережено
    assert store.records[photo["id"]].kind == "image"
    assert store.read_bytes(photo["id"]) == b"\x00heic-bytes"
    pic = store.ingest("скан_аналізу.jpg", b"jpg-bytes", origin="andrii_direct")
    assert pic["status"] == "stored" and store.records[pic["id"]].kind == "image"
    assert store.read_bytes(pic["id"]) == b"jpg-bytes"
    song = store.ingest("Лекція.FLAC", b"flac-bytes", text="тренування")
    assert song["status"] == "needs_engine" and store.records[song["id"]].kind == "audio"
    assert store.read_bytes(song["id"]) == b"flac-bytes"


def test_rewrite_stores_new_version_bytes(store: KodexStore) -> None:
    r = store.ingest("нотатка.md", b"old", text="ринок")
    store.rewrite(r["id"], b"new text", "очистка", actor="sam")
    assert store.read_bytes(r["id"]) == b"new text"


def test_purge_removes_unused_blob(store: KodexStore) -> None:
    r = store.ingest("тимчасове.png", b"tmp-img")
    path = store._blob_path(sha256_of(b"tmp-img"), "png")
    assert path.exists()
    store.request_delete(r["id"], actor="kodex")
    store.purge_expired(datetime.now() + timedelta(days=kodex.TRASH_RETENTION_DAYS + 1))
    assert not path.exists()


def test_state_and_blobs_survive_reload(tmp_path: Path) -> None:
    s = KodexStore(tmp_path / "k.json")
    r = s.ingest("голос.mp3", b"mp3-data", origin="andrii_kodex")
    s.save()
    again = KodexStore(tmp_path / "k.json")
    assert again.records[r["id"]].kind == "audio"
    assert again.read_bytes(r["id"]) == b"mp3-data"
