"""Fin — автоматичний виклик від Єви: валідація запиту і відповідь funds_answer.

Потік: Єва сформувала кошик → оркестратор отримує `eva_basket_ready` → Фін відповідає Єві
автоматично (без ручного кроку). Андрій може запитати напряму (`fin_funds_check`).

Чистий Python. Нічого не платить, не переказує, не замовляє. Приймає лише суми й категорії,
платіжних реквізитів не приймає.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional

from src.agents import fin_ledger as L
from src.agents import fin_policy as fp

# Поля, яких у запиті бути не може: Фін не отримує реквізити.
FORBIDDEN_FIELDS = frozenset({"card", "card_number", "pan", "iban", "cvv", "login",
                              "password", "account_number", "phone", "token"})


def validate_request(payload: Dict[str, Any], sender: str) -> Optional[str]:
    """Повертає причину відмови або None, якщо запит прийнятний."""
    if not L.route_allowed(sender, "funds_check"):
        return "sender_not_allowed"
    leaked = FORBIDDEN_FIELDS & set(payload)
    if leaked:
        return f"payment_fields_not_accepted:{sorted(leaked)[0]}"
    try:
        amount = Decimal(str(payload.get("amount")))
    except Exception:  # noqa: BLE001
        return "bad_amount"
    if amount <= 0:
        return "bad_amount"
    if payload.get("category", "other") not in L.CATEGORIES:
        return "unknown_category"
    fund = payload.get("fund")
    if fund is not None and fund not in L.PURCHASE_FUNDS and fund != "safety":
        return "unknown_fund"
    return None


def planned_from_config(items: Iterable[Dict[str, Any]]) -> List[L.PlannedPayment]:
    out = []
    for it in items:
        it = dict(it)
        if it.get("on"):
            it["on"] = date.fromisoformat(it["on"])
        it["amount"] = Decimal(str(it["amount"]))
        out.append(L.PlannedPayment(**it))
    return out


def planned_by_fund(payments: List[L.PlannedPayment], today: date) -> Dict[str, Decimal]:
    """Заплановано до кінця місяця по фондах (лише UAH — інші валюти не складаються)."""
    _, end = L.period_bounds(today, "month")
    items = L.plan_items(payments, today, end)
    out: Dict[str, Decimal] = {f: Decimal("0") for f in L.FUNDS}
    for it in items:
        if it["currency"] == "UAH":
            out[it["fund"]] += Decimal(it["amount"])
    return out


def answer_funds_check(payload: Dict[str, Any], sender: str, fund_balances: Dict[str, Any],
                       payments: List[L.PlannedPayment], today: date) -> Dict[str, Any]:
    """funds_answer для Єви (або Андрія). Лише рахує рекомендацію."""
    to = "andrii" if sender == "andrii" else "eva"
    reason = validate_request(payload, sender)
    if reason:
        return {"type": "funds_answer", "from": "fin", "to": to, "status": "rejected",
                "reason": reason, "advisory_only": True}

    amount = Decimal(str(payload["amount"]))
    currency = payload.get("currency", "UAH")
    base = {"type": "funds_answer", "from": "fin", "to": to, "amount": str(amount),
            "currency": currency, "category": payload.get("category", "other"),
            "purpose": payload.get("purpose", ""), "advisory_only": True}
    if currency != "UAH":
        return {**base, "status": "currency_needs_conversion",
                "note": "Сума в іншій валюті: конвертацію і курс не вигадуємо."}

    _, month_end = L.period_bounds(today, "month")
    planned = planned_by_fund(payments, today)
    left = {}
    for f in L.FUNDS:
        bal = Decimal(str(fund_balances.get(f, 0)))
        left[f] = L.available_in_fund(bal, planned[f])
    res = fp.allocate_purchase(amount, payload.get("category", "other"),
                               {k: v for k, v in left.items()}, payload.get("purpose", ""),
                               fund=payload.get("fund"), valid_until=month_end.isoformat())
    return {**base, **res, "to": to, "from": "fin", "type": "funds_answer", "advisory_only": True,
            "available_by_fund": {k: str(v) for k, v in left.items() if k != "safety"}}


def unavailable_answer(payload: Dict[str, Any], sender: str) -> Dict[str, Any]:
    """Немає залишків (банк закритий, ручних даних нема): нічого не вигадуємо."""
    to = "andrii" if sender == "andrii" else "eva"
    return {"type": "funds_answer", "from": "fin", "to": to, "status": "unavailable",
            "reason": "no_fund_balances", "advisory_only": True,
            "purpose": payload.get("purpose", ""),
            "message": "Залишки не отримано: читання банку не дозволене, ручних даних немає."}
