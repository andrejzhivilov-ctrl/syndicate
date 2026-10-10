"""Fin — шлюз банківського читання (рішення A: за замовчуванням закрито).

Читання банку дозволене лише для провайдерів, явно перелічених у конфігурації
(`bank_read_grants`). Порожній список = жодного звернення до банку. Ніяких записів.
Ручне введення виписок — не доступ до банку, воно не проходить через цей шлюз.
"""

from __future__ import annotations

from typing import Iterable

KNOWN_PROVIDERS = frozenset({"monobank", "privatbank", "a_bank"})


def bank_read_allowed(provider: str, grants: Iterable[str]) -> bool:
    return provider in KNOWN_PROVIDERS and provider in set(grants)


def denied_reply(provider: str) -> dict:
    return {"status": "unavailable", "error": "bank_read_not_granted", "provider": provider,
            "write_allowed": False}
