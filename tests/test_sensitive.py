"""Operator decision 29.10: military talk, account numbers and access codes stay out of voice."""
from __future__ import annotations

import asyncio

import pytest

from src.agent_chat import MILITARY_NOTE, ChatHistory, chat_reply
from src.sensitive import VOICE_NOTICE, is_military, mask_for_voice, voice_text

OPERATIONAL = [
    "Завтра о 6:00 рота переміщується з Покровська на нові позиції біля траси.",
    "Брат служить у 47-й бригаді, вони зараз стоять під Авдіївкою, просив передати дрон Mavic.",
    "Координати точки: 48.2851, 37.1834",
    "Батальйон висувається на опорний пункт уночі.",
]
NOT_OPERATIONAL = [
    "Новини: ЗСУ звільнили село на Харківщині, повідомляє Генштаб.",
    "Скільки коштує підписка на Notion для команди з п'яти людей?",
    "Наш дохід за жовтень 12 400 євро, витрати 9 100, хочу вкласти решту в ETF.",
    "Яка позиція нашого бренду на ринку кави?",
    "Переведи 2500 доларів Олегу, його телефон +380671234567.",
]


@pytest.mark.parametrize("text", OPERATIONAL)
def test_operational_military_detail_is_detected(text):
    assert is_military(text)


@pytest.mark.parametrize("text", NOT_OPERATIONAL)
def test_news_money_and_business_are_not_military(text):
    assert not is_military(text)


def test_account_numbers_and_codes_are_masked_but_the_rest_is_voiced():
    reply = ("Залишок 184 тисячі. IBAN UA213223130000026007233566001, картка 4111 1111 1111 1111, "
             "рахунок № 26007233566001, PIN 4821. Решта витрат у нормі.")
    spoken, kinds = mask_for_voice(reply)
    for raw in ("UA2132", "4111", "26007233566001", "4821"):
        assert raw not in spoken
    assert "Залишок 184 тисячі" in spoken and spoken.endswith("Решта витрат у нормі.")
    assert {"номер рахунку", "номер картки", "код доступу"} <= set(kinds)


def test_phone_and_plain_amounts_are_not_mistaken_for_cards():
    text = "Подзвони +380671234567, бюджет 12 400 євро, замовлення 2026-10-29."
    assert mask_for_voice(text) == (text, [])


def test_military_or_secret_replies_are_never_voiced():
    assert voice_text("де зараз стоїть наша рота на позиції?", "Не варто це обговорювати.") == (
        VOICE_NOTICE, "military")
    assert voice_text("", "password: Hunter2-long")[1] == "secret"
    assert voice_text("Як справи?", "Усе добре, бюджет 370 доларів.") == ("Усе добре, бюджет 370 доларів.", "plain")


class _LLM:
    def __init__(self):
        self.calls = []

    async def ainvoke(self, messages):
        self.calls.append(messages)
        return "Такі деталі краще не передавати через систему."


def test_agent_gets_the_military_note_and_does_not_remember_the_turn():
    llm, history = _LLM(), ChatHistory(None)
    result = asyncio.run(chat_reply("fin", OPERATIONAL[1], llm, history, "523"))
    assert result["status"] == "completed" and result["military_trigger"] is True
    assert ("system", MILITARY_NOTE) in llm.calls[0]
    assert asyncio.run(history.load("fin", "523")) == []

    asyncio.run(chat_reply("fin", "Який бюджет на жовтень?", llm, history, "523"))
    assert ("system", MILITARY_NOTE) not in llm.calls[1]
    assert len(asyncio.run(history.load("fin", "523"))) == 2
