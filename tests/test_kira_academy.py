"""Академія Кіри: каталог, чесність без LLM, самонавчання, пропозиції, кнопки."""

from __future__ import annotations

import asyncio
import copy
from pathlib import Path

import pytest

from src.agents import kira_buttons as kb
from src.agents.kira import KiraAgent
from src.agents.kira_catalog import CatalogError, build_catalog, load_seed
from src.agents.kira_learning import KiraLearningStore, MIN_ANSWERS_FOR_STATS


def _run(coro):
    return asyncio.run(coro)


class _Reply:
    def __init__(self, content: str) -> None:
        self.content = content


class _StubLLM:
    def __init__(self, text: str = "відповідь моделі") -> None:
        self.text = text
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        return _Reply(self.text)


class _BrokenLLM:
    async def ainvoke(self, messages):
        raise RuntimeError("provider down")


@pytest.fixture
def store(tmp_path: Path) -> KiraLearningStore:
    return KiraLearningStore(tmp_path / "kira_learning.json")


@pytest.fixture
def kira(store: KiraLearningStore) -> KiraAgent:
    return KiraAgent(memory=None, llm=None, learning=store)


# ------------------------------------------------------------ каталог

def test_seed_catalog_is_valid_and_has_five_disciplines() -> None:
    catalog = build_catalog(load_seed())
    assert set(catalog["disciplines"]) == {"english", "programming", "ai_engineering", "vibecoding", "history"}
    assert catalog["quiz_bank"], "банк питань порожній"
    for kind in ("word_of_the_day", "coding_spark", "history_model"):
        assert catalog["morning_items"][kind]


def test_quiz_items_have_verifiable_answer_keys() -> None:
    catalog = build_catalog(load_seed())
    for item in catalog["quiz_bank"]:
        assert item["answer"] in item["options"]
        assert item["topic"] in catalog["disciplines"][item["discipline"]]["topics"]


def test_catalog_rejects_topic_outside_discipline() -> None:
    seed = load_seed()
    seed["quiz_bank"][0]["topic"] = "Не існуюча тема"
    with pytest.raises(CatalogError):
        build_catalog(seed)


def test_catalog_rejects_wrong_option_keys_and_duplicate_ids() -> None:
    seed = load_seed()
    bad = copy.deepcopy(seed)
    bad["quiz_bank"][0]["options"].pop("D")
    with pytest.raises(CatalogError):
        build_catalog(bad)
    dup = copy.deepcopy(seed)
    dup["quiz_bank"].append(copy.deepcopy(dup["quiz_bank"][0]))
    with pytest.raises(CatalogError):
        build_catalog(dup)


# ------------------------------------------------------------ чесність без LLM

def test_llm_actions_without_llm_are_unavailable_not_fabricated(kira: KiraAgent) -> None:
    cases = [
        {"action": "socratic_dialogue", "statement": "x"},
        {"action": "code_review", "code": "def f(): pass"},
        {"action": "language_practice", "user_input": "We build agents."},
        {"action": "history_synthesis", "query": "Рим"},
        {"action": "vibecoding_session", "concept": "бот"},
    ]
    for payload in cases:
        out = _run(kira.execute(payload))
        assert out["status"] == "unavailable", payload["action"]
        assert out["reason"] == "llm_not_configured"
        assert "confidence" not in out
        for field in ("socratic_response", "review", "feedback", "historical_synthesis", "vibecoding_brief"):
            assert field not in out


def test_lesson_plan_without_llm_is_skeleton_only(kira: KiraAgent) -> None:
    out = _run(kira.execute({"action": "lesson_plan", "discipline": "programming"}))
    assert out["status"] == "partial"
    assert out["curriculum"] is None
    assert out["skeleton"]["module_1_fundamentals"]


def test_llm_error_is_reported_as_error_not_content(store: KiraLearningStore) -> None:
    agent = KiraAgent(memory=None, llm=_BrokenLLM(), learning=store)
    out = _run(agent.execute({"action": "socratic_dialogue", "statement": "x"}))
    assert out["status"] == "unavailable" and out["reason"] == "llm_error"


def test_llm_actions_with_llm_return_model_text(store: KiraLearningStore) -> None:
    llm = _StubLLM("Ось питання.")
    agent = KiraAgent(memory=None, llm=llm, learning=store)
    out = _run(agent.execute({"action": "socratic_dialogue", "statement": "x"}))
    assert out["status"] == "ok" and out["socratic_response"] == "Ось питання."
    assert llm.calls == 1


def test_code_review_requires_code(kira: KiraAgent) -> None:
    out = _run(kira.execute({"action": "code_review"}))
    assert out["status"] == "unavailable" and out["reason"] == "code_required"


# ------------------------------------------------------------ квіз і самонавчання

def test_quiz_question_hides_answer_key(kira: KiraAgent) -> None:
    out = _run(kira.execute({"action": "micro_quiz", "discipline": "programming"}))
    assert out["status"] == "ok"
    assert "answer" not in out["question"] and "explanation" not in out["question"]
    assert set(out["question"]["options"]) == {"A", "B", "C", "D"}


def test_answer_is_checked_against_key(kira: KiraAgent, store: KiraLearningStore) -> None:
    item = store.catalog()["quiz_bank"][0]
    wrong = next(k for k in item["options"] if k != item["answer"])
    out = _run(kira.execute({"action": "micro_quiz_answer", "question_id": item["id"], "choice": wrong}))
    assert out["status"] == "recorded" and out["correct"] is False
    assert out["correct_answer"] == item["answer"]
    ok = _run(kira.execute({"action": "micro_quiz_answer", "question_id": item["id"], "choice": item["answer"]}))
    assert ok["correct"] is True


def test_accuracy_is_none_until_enough_answers(store: KiraLearningStore) -> None:
    item = store.catalog()["quiz_bank"][0]
    wrong = next(k for k in item["options"] if k != item["answer"])
    for _ in range(MIN_ANSWERS_FOR_STATS - 1):
        store.record_answer(item["id"], wrong)
    row = store.topic_stats()[f"{item['discipline']}/{item['topic']}"]
    assert row["accuracy"] is None and "note" in row
    assert store.weak_topics() == []


def test_weak_topic_is_preferred_for_next_question(store: KiraLearningStore) -> None:
    catalog = store.catalog()
    prog = [q for q in catalog["quiz_bank"] if q["discipline"] == "programming"]
    target_topic = prog[0]["topic"]
    same_topic = [q for q in prog if q["topic"] == target_topic]
    for q in same_topic:
        wrong = next(k for k in q["options"] if k != q["answer"])
        for _ in range(MIN_ANSWERS_FOR_STATS):
            store.record_answer(q["id"], wrong)
    assert f"programming/{target_topic}" in store.weak_topics()
    nxt = store.next_quiz_item("programming")
    assert nxt is not None and nxt["topic"] == target_topic


def test_answer_without_store_is_unavailable_not_recorded(tmp_path: Path) -> None:
    agent = KiraAgent(memory=None, learning=KiraLearningStore(None))
    out = _run(agent.execute({"action": "micro_quiz_answer", "question_id": "prog-breaker-01", "choice": "B"}))
    assert out["status"] == "unavailable"


def test_learning_persists_answers_and_approved_items(tmp_path: Path) -> None:
    path = tmp_path / "kl.json"
    s1 = KiraLearningStore(path)
    s1.record_answer("prog-breaker-01", "B")
    s2 = KiraLearningStore(path)
    assert len(s2.answers) == 1


# ------------------------------------------------------------ пропозиції: лише Андрій схвалює

def test_proposal_is_pending_and_only_andrii_can_approve(kira: KiraAgent, store: KiraLearningStore) -> None:
    prop = _run(kira.execute({
        "action": "propose_learning",
        "kind": "new_discipline",
        "reason": "Андрій хоче дисципліну про фінанси",
        "payload": {
            "key": "finance",
            "title": "Фінанси",
            "icon": "💰",
            "focus": "Унит-економіка",
            "topics": ["Unit economics"],
        },
    }))
    assert prop["status"] == "pending"
    before = set(store.catalog()["disciplines"])
    denied = _run(kira.execute({"action": "decide_proposal", "proposal_id": prop["proposal_id"],
                                "decision": "approve", "actor": "eva"}))
    assert denied["status"] == "rejected" and denied["reason"] == "only_andrii_decides"
    assert set(store.catalog()["disciplines"]) == before
    ok = _run(kira.execute({"action": "decide_proposal", "proposal_id": prop["proposal_id"],
                            "decision": "approve", "actor": "andrii"}))
    assert ok["status"] == "approved"
    assert "finance" in store.catalog()["disciplines"]


def test_invalid_proposal_is_rejected_before_storage(kira: KiraAgent, store: KiraLearningStore) -> None:
    out = _run(kira.execute({
        "action": "propose_learning",
        "kind": "new_quiz_item",
        "reason": "тест",
        "payload": {"id": "bad-item-01", "discipline": "programming", "topic": "Неіснуюча",
                    "question": "q", "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
                    "answer": "A", "explanation": "e"},
    }))
    assert out["status"] == "rejected" and out["reason"] == "invalid_payload"
    assert store.pending() == []


def test_approved_quiz_item_appears_in_bank(kira: KiraAgent, store: KiraLearningStore) -> None:
    prop = _run(kira.execute({
        "action": "propose_learning",
        "kind": "new_quiz_item",
        "reason": "нове питання",
        "payload": {"id": "prog-new-01", "discipline": "programming", "topic": "Concurrency & AsyncIO",
                    "question": "Яка функція створює задачу?",
                    "options": {"A": "asyncio.create_task", "B": "time.sleep", "C": "print", "D": "open"},
                    "answer": "A", "explanation": "create_task планує корутину як задачу."},
    }))
    _run(kira.execute({"action": "decide_proposal", "proposal_id": prop["proposal_id"],
                       "decision": "approve", "actor": "andrii"}))
    ids = [q["id"] for q in store.catalog()["quiz_bank"]]
    assert "prog-new-01" in ids


def test_proposal_kind_must_be_known(kira: KiraAgent) -> None:
    out = _run(kira.execute({"action": "propose_learning", "kind": "change_permissions",
                             "reason": "x", "payload": {}}))
    assert out["status"] == "rejected" and out["reason"] == "unknown_kind"


# ------------------------------------------------------------ ранкова іскра

def test_morning_spark_is_deterministic_per_date(kira: KiraAgent) -> None:
    a = _run(kira.execute({"action": "morning_data", "date": "2026-10-14"}))
    b = _run(kira.execute({"action": "morning_data", "date": "2026-10-14"}))
    assert a["status"] == "ok" and a == b
    assert a["sources"]["word_of_the_day"] in ("dossier", "seed_needs_andrii_review")


def test_morning_spark_rejects_bad_date(kira: KiraAgent) -> None:
    out = _run(kira.execute({"action": "morning_data", "date": "14.10.2026"}))
    assert out["status"] == "rejected"


def test_dispatch_unknown_action_still_error(kira: KiraAgent) -> None:
    out = _run(kira.execute({"action": "nope"}))
    assert out["status"] == "error"
    assert "micro_quiz_answer" in out["available_actions"]


# ------------------------------------------------------------ кнопки Telegram

OWNERS = ["111"]


def test_buttons_refuse_non_owner_and_empty_allowlist() -> None:
    assert kb.parse_callback("kira:act:quiz", "999", OWNERS)["ok"] is False
    assert kb.parse_callback("kira:act:quiz", "111", [])["ok"] is False


def test_buttons_map_to_actions() -> None:
    assert kb.parse_callback("kira:act:quiz", "111", OWNERS)["action"] == "micro_quiz"
    assert kb.parse_callback("kira:disc:history", "111", OWNERS) == {
        "ok": True, "action": "micro_quiz", "discipline": "history"}
    ans = kb.parse_callback("kira:ans:prog-breaker-01:B", "111", OWNERS)
    assert ans == {"ok": True, "action": "micro_quiz_answer", "question_id": "prog-breaker-01", "choice": "B"}


def test_proposal_buttons_always_act_as_andrii() -> None:
    out = kb.parse_callback("kira:prop:ab12cd34:ok", "111", OWNERS)
    assert out["action"] == "decide_proposal" and out["decision"] == "approve" and out["actor"] == "andrii"


def test_malformed_and_unknown_callbacks_are_refused() -> None:
    for bad in ("", "kira", "kira:act:delete_all", "kira:disc:unknown", "kira:ans:x:Z", "other:act:quiz"):
        assert kb.parse_callback(bad, "111", OWNERS)["ok"] is False, bad
    assert kb.parse_callback("kira:act:" + "x" * 80, "111", OWNERS)["ok"] is False


def test_answer_keyboard_fits_telegram_limit_for_seed_ids() -> None:
    for item in load_seed()["quiz_bank"]:
        kbd = kb.build_answer_keyboard(item["id"])
        assert kbd is not None, item["id"]
        for row in kbd:
            for btn in row:
                assert len(btn["callback_data"].encode("utf-8")) <= kb.CALLBACK_MAX_BYTES
