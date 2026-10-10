"""Fin — джерела коштів, фонди, витрати, планувальник платежів і маршрутизація.

Чистий Python без мережі й без банків. Фін лише рахує і показує; нічого не платить,
не переказує і не замовляє. Реквізитів (номерів карток, IBAN, логінів) тут немає.
ФОП — окрема документація, а не рахунок і не джерело коштів.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple

# ---------------------------------------------------------------- фонди
# Фонди = картки, готівковий фонд, платіжні системи. Назви уточнюються при налаштуванні
# доступів (поле label — плейсхолдер, не фінальна назва).
FUNDS: Dict[str, str] = {
    "card": "Картки (назви — при налаштуванні доступів)",
    "cash": "Готівковий фонд",
    "payment_system": "Платіжні системи (назви — при налаштуванні доступів)",
    "safety": "Фонд безпеки (недоторканний)",
}
PURCHASE_FUNDS = ("card", "cash", "payment_system")  # порядок автовибору
RESERVED_FUNDS = frozenset({"safety"})                # ніколи не джерело покупки
# Категорії витрат (не фонди).
CATEGORIES: Dict[str, str] = {"food": "Продукти", "leisure": "Відпочинок", "other": "Інше"}

# ---------------------------------------------------------------- джерела коштів
# cash_path: як гроші стають готівкою. Порядок пріоритету — з найпростішого.
CASH_PATH_PRIORITY = {"already_cash": 0, "direct_atm": 1, "via_bank_transfer": 2, "via_exchange": 3}

SOURCES: Dict[str, dict] = {
    "cash_wallet": {"label": "Готівка (гаманець)", "kind": "cash", "currency": "UAH",
                    "cash_path": "already_cash", "intl": False, "fund": "cash",
                    "note": "Переказ Assets:Bank → Assets:Cash:Wallet"},
    "monobank": {"fund": "card", "label": "Монобанк (картка)", "kind": "bank", "currency": "UAH",
                 "cash_path": "direct_atm", "intl": False, "read_mode": "not_granted"},
    "privatbank": {"fund": "card", "label": "ПриватБанк (картка)", "kind": "bank", "currency": "UAH",
                   "cash_path": "direct_atm", "intl": False, "read_mode": "not_granted"},
    "a_bank": {"fund": "card", "label": "А-Банк", "kind": "bank", "currency": "UAH",
               "cash_path": "direct_atm", "intl": False, "read_mode": "not_connected",
               "note": "Окрема інтеграція (AISP з NBU-ліцензією), не в коді"},
    "payoneer": {"fund": "payment_system", "label": "Payoneer", "kind": "payment_service", "currency": "USD",
                 "cash_path": "via_bank_transfer", "intl": True, "read_mode": "not_connected",
                 "note": "Міжнародні перекази; вивід на банк з комісією і курсом"},
    "paypal": {"fund": "payment_system", "label": "PayPal", "kind": "payment_service", "currency": "USD",
               "cash_path": "via_bank_transfer", "intl": True, "read_mode": "not_connected",
               "note": "Міжнародні перекази; вивід на банк з комісією"},
    "crypto_wallet": {"fund": "payment_system", "label": "Криптогаманець", "kind": "crypto", "currency": "USDT",
                      "cash_path": "via_exchange", "intl": True, "read_mode": "not_connected",
                      "note": "Потрібен обмін на фіат; курс і комісія ризиковані"},
}


def withdraw_options(amount: Decimal, currency: str,
                     balances: Dict[str, Tuple[Decimal, str]]) -> List[dict]:
    """З якого джерела можна отримати `amount` готівкою.

    balances: {source_id: (сума, валюта)} — дає Андрій або Фін з дозволеного читання.
    Повертає список від найпростішого до найскладнішого. Без балансу джерело НЕ
    вважається доступним (не вигадуємо).
    """
    need = Decimal(str(amount))
    out: List[dict] = []
    for sid, meta in SOURCES.items():
        if sid not in balances:
            continue
        bal, cur = balances[sid]
        bal = Decimal(str(bal))
        if cur != currency:  # сума в іншій валюті — потрібна конвертація, не вигадуємо курс
            status = "needs_conversion"
        elif bal >= need:
            status = "enough"
        else:
            status = "insufficient"
        out.append({"source": sid, "label": meta["label"], "status": status,
                    "balance": str(bal), "currency": cur,
                    "cash_path": meta["cash_path"], "intl": meta["intl"], "fund": meta["fund"],
                    "_prio": CASH_PATH_PRIORITY[meta["cash_path"]]})
    out.sort(key=lambda r: (r["status"] != "enough", r["_prio"]))
    for r in out:
        r.pop("_prio")
    return out


def available_in_fund(fund_balance: Decimal, planned_in_period: Decimal) -> Decimal:
    """Доступно під покупку = залишок фонду мінус уже заплановані платежі цього періоду."""
    return Decimal(str(fund_balance)) - Decimal(str(planned_in_period))


# ---------------------------------------------------------------- витрати
@dataclass
class Expense:
    on: date
    amount: Decimal
    currency: str
    fund: str
    category: str
    purpose: str
    store: str = ""
    source: str = ""          # id джерела (без реквізитів)
    ordered_by: str = "andrii"

    def __post_init__(self) -> None:
        if self.fund not in FUNDS:
            raise ValueError(f"unknown fund: {self.fund}")
        if self.fund in RESERVED_FUNDS:
            raise ValueError("safety fund cannot be a purchase source")
        self.amount = Decimal(str(self.amount))


def period_bounds(today: date, period: str) -> Tuple[date, date]:
    if period == "day":
        return today, today
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    if period == "month":
        last = calendar.monthrange(today.year, today.month)[1]
        return today.replace(day=1), today.replace(day=last)
    raise ValueError(f"unknown period: {period}")


def spend_by_fund(expenses: Iterable[Expense], start: date, end: date) -> Dict[str, Decimal]:
    totals: Dict[str, Decimal] = {f: Decimal("0") for f in FUNDS}
    for e in expenses:
        if start <= e.on <= end:
            totals[e.fund] += e.amount
    return totals


# ---------------------------------------------------------------- планувальник
CADENCES = ("once", "day", "week", "month")
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "нд"]


@dataclass
class PlannedPayment:
    id: str
    name: str
    amount: Decimal
    currency: str
    cadence: str                      # once | day | week | month
    fund: str = "card"
    on: Optional[date] = None         # для once
    weekday: Optional[int] = None     # 0=пн для week
    day_of_month: Optional[int] = None  # 1..31 для month (обрізається до кінця місяця)

    def __post_init__(self) -> None:
        if self.cadence not in CADENCES:
            raise ValueError(f"bad cadence: {self.cadence}")
        if self.fund not in FUNDS:
            raise ValueError(f"unknown fund: {self.fund}")
        self.amount = Decimal(str(self.amount))

    def occurrences(self, start: date, end: date) -> List[date]:
        if self.cadence == "once":
            return [self.on] if self.on and start <= self.on <= end else []
        days: List[date] = []
        d = start
        while d <= end:
            if self.cadence == "day":
                days.append(d)
            elif self.cadence == "week" and d.weekday() == self.weekday:
                days.append(d)
            elif self.cadence == "month":
                last = calendar.monthrange(d.year, d.month)[1]
                if d.day == min(self.day_of_month, last):
                    days.append(d)
            d += timedelta(days=1)
        return days


def plan_items(payments: Iterable[PlannedPayment], start: date, end: date) -> List[dict]:
    rows = []
    for p in payments:
        for d in p.occurrences(start, end):
            rows.append({"date": d.isoformat(), "name": p.name, "amount": str(p.amount),
                         "currency": p.currency, "fund": p.fund, "cadence": p.cadence,
                         "payment_id": p.id})
    rows.sort(key=lambda r: (r["date"], r["name"]))
    return rows


def plan_totals(items: Iterable[dict]) -> Dict[str, str]:
    """Сума по валютах. Змішані валюти не складаються між собою."""
    tot: Dict[str, Decimal] = {}
    for r in items:
        tot[r["currency"]] = tot.get(r["currency"], Decimal("0")) + Decimal(r["amount"])
    return {k: str(v.quantize(Decimal("0.01"))) for k, v in sorted(tot.items())}


def plan_header(payments: Iterable[PlannedPayment], today: date) -> Dict[str, dict]:
    """Завжди показується у звітах: що заплановано на день, тиждень, місяць і разом."""
    payments = list(payments)
    out = {}
    for period in ("day", "week", "month"):
        s, e = period_bounds(today, period)
        items = plan_items(payments, s, e)
        out[period] = {"from": s.isoformat(), "to": e.isoformat(),
                       "count": len(items), "totals": plan_totals(items)}
    # Загально — на наступні 30 днів від сьогодні
    items = plan_items(payments, today, today + timedelta(days=29))
    out["next_30_days"] = {"from": today.isoformat(),
                           "to": (today + timedelta(days=29)).isoformat(),
                           "count": len(items), "totals": plan_totals(items)}
    return out


# ---------------------------------------------------------------- маршрутизація
# Фін відповідає ЛИШЕ Єві (і Андрію напряму). Єва не призначає Фіну інших задач.
ROUTES = {
    "eva": {"funds_check", "basket_status", "expense_note", "report_request"},
    "andrii": {"*"},
}
REPLY_TO_EVA = {"funds_answer", "plan_brief", "morning_brief"}


def route_allowed(sender: str, msg_type: str) -> bool:
    allowed = ROUTES.get(sender)
    if not allowed:
        return False
    return "*" in allowed or msg_type in allowed
