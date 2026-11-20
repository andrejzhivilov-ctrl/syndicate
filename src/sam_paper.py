"""Sam's paper accounts: trades and bets with no real money, fully autonomous (Andrii, 19.11.2026).

Andrii: on paper Sam trades and bets by himself, scalping included, so that a month of honest numbers
decides where real money goes. This module is that ledger. It never touches a broker or a bookmaker.

- Accounts (Andrii's amounts): trading $100, crypto $100 (a "new projects" basket inside it), bets
  1000 UAH, investing 3000 UAH.
- A trade has a strategy tag, entry, stop and target; its size comes from the risk per trade and the
  stop distance, capped by leverage (x10 on paper, as Andrii asked); costs are charged on both sides.
- Open trades are marked against candles: a stop or target hit closes them (if both in one candle, the
  stop counts: the worse case). Losses past Andrii's limits freeze new trades on that account.
- A bet is sized by a quarter Kelly capped at 2% of the bank; when it settles, CLV is kept.
- Statistics per strategy decide the tournament: trades, win rate, profit factor, expectancy in R,
  maximum drawdown — all from the ledger, never from a model's estimate.
"""
from __future__ import annotations

import json
import math
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.data_paths import ensure_dir

ACCOUNTS: Dict[str, Dict[str, Any]] = {
    "trading": {"start": 100.0, "currency": "USD", "max_leverage": 10, "cost_bps": 3},
    "crypto": {"start": 100.0, "currency": "USD", "max_leverage": 10, "cost_bps": 10},
    "invest": {"start": 3000.0, "currency": "UAH", "max_leverage": 1, "cost_bps": 5},
    "bets": {"start": 1000.0, "currency": "UAH"},
}
#: Andrii's limits (19.11.2026): day, week, month, total.
LOSS_LIMITS = {"day": 0.03, "week": 0.06, "month": 0.10, "total": 0.20}
MAX_RISK = {"trading": 0.01, "crypto": 0.01, "invest": 0.10}
#: 20.11.2026: the first night of one-minute scalps lost 2-3.4R a stop and even a hit target closed below zero,
#: because the round-trip costs were larger than the stop distance. A trade whose costs take more than this
#: share of its risk is refused: with costs at 0.2R the 2.5R target still pays, below that nothing can.
MAX_COST_R = 0.20


def cost_in_r(account: str, entry: float, stop: float, target: float) -> float:
    """Entry and exit costs of the paper account, in units of the trade's risk."""
    cost = ACCOUNTS[account]["cost_bps"] / 10_000
    return (entry + target) * cost / abs(entry - stop)
#: New, unproven crypto projects: allowed on paper in their own small basket (Andrii, 19.11.2026).
NEW_PROJECT_STRATEGY = "new_project"
NEW_PROJECT_SHARE = 0.10
MAX_BET_SHARE = 0.02
KELLY_FRACTION = 0.25
MAX_BETS_PER_DAY = 10


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _path() -> Path:
    return ensure_dir("sam_paper") / "ledger.json"


def load() -> Dict[str, Any]:
    try:
        return json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"open": [], "closed": [], "bets": [], "settled": []}


def save(ledger: Dict[str, Any]) -> None:
    path = _path()
    spare = path.with_suffix(".tmp")
    spare.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    spare.replace(path)


def balance(ledger: Dict[str, Any], account: str) -> float:
    if account == "bets":
        return ACCOUNTS["bets"]["start"] + sum(b["pnl"] for b in ledger["settled"])
    return ACCOUNTS[account]["start"] + sum(t["pnl"] for t in ledger["closed"] if t["account"] == account)


def _since(ledger: Dict[str, Any], account: str, start: datetime) -> float:
    rows = ledger["settled"] if account == "bets" else [t for t in ledger["closed"] if t["account"] == account]
    return sum(r["pnl"] for r in rows if datetime.fromisoformat(r["closed_at"]) >= start)


def frozen(ledger: Dict[str, Any], account: str, now: Optional[datetime] = None) -> Optional[str]:
    """The limit that stops new trades on this account now, or None."""
    now = now or _now()
    start = ACCOUNTS[account]["start"]
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    windows = {"day": day, "week": day - timedelta(days=day.weekday()), "month": day.replace(day=1),
               "total": datetime(1970, 1, 1, tzinfo=timezone.utc)}
    for name, since in windows.items():
        if _since(ledger, account, since) <= -LOSS_LIMITS[name] * start:
            return name
    return None


# ── trades ────────────────────────────────────────────────────────────────────────────────


def _plan_problem(account: str, side: str, entry: float, stop: float, target: float, risk: float) -> Optional[Dict[str, Any]]:
    """Why this trade plan cannot be opened at all, or None."""
    if account not in ACCOUNTS or account == "bets":
        return {"status": "error", "error": "unknown_account", "available": [a for a in ACCOUNTS if a != "bets"]}
    if side not in ("long", "short"):
        return {"status": "error", "error": "side_must_be_long_or_short"}
    if not all(isinstance(x, (int, float)) and math.isfinite(x) and x > 0 for x in (entry, stop, target)):
        return {"status": "error", "error": "prices_must_be_positive_numbers"}
    if (side == "long" and not stop < entry < target) or (side == "short" and not target < entry < stop):
        return {"status": "error", "error": "stop_and_target_on_wrong_sides"}
    if min(float(risk), MAX_RISK[account]) <= 0:
        return {"status": "error", "error": "risk_must_be_positive"}
    cost_r = cost_in_r(account, entry, stop, target)
    if cost_r > MAX_COST_R:
        return {"status": "refused", "reason": "costs_eat_the_edge", "cost_r": round(cost_r, 3), "max_cost_r": MAX_COST_R,
                "hint": "стоп надто близько для цих комісій: ширший стоп або старший таймфрейм"}
    return None


def open_trade(ledger: Dict[str, Any], *, account: str, strategy: str, source: str, symbol: str, side: str,
               entry: float, stop: float, target: float, risk: float, timeframe: str = "", reason: str = "",
               leverage: Optional[float] = None, now: Optional[datetime] = None) -> Dict[str, Any]:
    problem = _plan_problem(account, side, entry, stop, target, risk)
    if problem:
        return problem
    risk = min(float(risk), MAX_RISK[account])
    limit = frozen(ledger, account, now)
    if limit:
        return {"status": "refused", "reason": f"loss_limit_{limit}", "account": account}
    equity = balance(ledger, account)
    if strategy == NEW_PROJECT_STRATEGY:
        used = sum(t["entry"] * t["size"] / t["leverage"] for t in ledger["open"] if t["strategy"] == NEW_PROJECT_STRATEGY)
        if used >= NEW_PROJECT_SHARE * equity:
            return {"status": "refused", "reason": "new_project_basket_full"}
    size = equity * risk / abs(entry - stop)
    max_lev = ACCOUNTS[account]["max_leverage"]
    lev = min(float(leverage or max_lev), max_lev)
    if size * entry > equity * lev:
        size = equity * lev / entry  # the leverage cap wins over the risk size
    trade = {"id": uuid.uuid4().hex[:10], "account": account, "strategy": strategy, "source": source,
             "symbol": symbol, "side": side, "timeframe": timeframe, "entry": entry, "stop": stop, "target": target,
             "size": size, "leverage": lev, "risk_money": round(size * abs(entry - stop), 6),
             "reason": reason[:500], "opened_at": (now or _now()).isoformat()}
    ledger["open"].append(trade)
    return {"status": "ok", "trade": trade}


def _close(ledger: Dict[str, Any], trade: Dict[str, Any], price: float, why: str, now: Optional[datetime]) -> Dict[str, Any]:
    direction = 1 if trade["side"] == "long" else -1
    gross = direction * (price - trade["entry"]) * trade["size"]
    cost = (trade["entry"] + price) * trade["size"] * ACCOUNTS[trade["account"]]["cost_bps"] / 10_000
    pnl = gross - cost
    closed = {**trade, "exit": price, "exit_reason": why, "pnl": round(pnl, 6), "cost": round(cost, 6),
              "r": round(pnl / trade["risk_money"], 3) if trade["risk_money"] else 0.0,
              "closed_at": (now or _now()).isoformat()}
    ledger["open"] = [t for t in ledger["open"] if t["id"] != trade["id"]]
    ledger["closed"].append(closed)
    return closed


def close_trade(ledger: Dict[str, Any], trade_id: str, price: float, why: str = "manual",
                now: Optional[datetime] = None) -> Dict[str, Any]:
    trade = next((t for t in ledger["open"] if t["id"] == trade_id), None)
    if trade is None:
        return {"status": "error", "error": "no_such_open_trade"}
    return {"status": "ok", "trade": _close(ledger, trade, float(price), why, now)}


def mark(ledger: Dict[str, Any], source: str, symbol: str, candles: List[Dict[str, Any]],
         now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Close open trades of this symbol whose stop or target a candle touched after they opened."""
    closed = []
    for trade in [t for t in ledger["open"] if t["source"] == source and t["symbol"] == symbol]:
        opened = datetime.fromisoformat(trade["opened_at"])
        for candle in candles:
            if candle["time"] < opened:
                continue
            long = trade["side"] == "long"
            hit_stop = candle["low"] <= trade["stop"] if long else candle["high"] >= trade["stop"]
            hit_target = candle["high"] >= trade["target"] if long else candle["low"] <= trade["target"]
            if hit_stop:  # both in one candle: the stop, the worse case
                closed.append(_close(ledger, trade, trade["stop"], "stop", now))
                break
            if hit_target:
                closed.append(_close(ledger, trade, trade["target"], "target", now))
                break
    return closed


# ── bets ──────────────────────────────────────────────────────────────────────────────────


def place_bet(ledger: Dict[str, Any], *, strategy: str, sport: str, event: str, market: str, selection: str,
              odds: float, probability: float, bookmaker: str = "", fair_odds: Optional[float] = None,
              now: Optional[datetime] = None) -> Dict[str, Any]:
    if not (odds > 1 and 0 < probability < 1):
        return {"status": "error", "error": "odds_above_1_and_probability_between_0_and_1"}
    limit = frozen(ledger, "bets", now)
    if limit:
        return {"status": "refused", "reason": f"loss_limit_{limit}"}
    today = (now or _now()).date().isoformat()
    if sum(1 for b in ledger["bets"] + ledger["settled"] if b["placed_at"][:10] == today) >= MAX_BETS_PER_DAY:
        return {"status": "refused", "reason": "ten_bets_a_day"}
    edge = probability * odds - 1
    if edge <= 0:
        return {"status": "refused", "reason": "no_positive_expectation", "ev": round(edge, 4)}
    kelly = edge / (odds - 1)
    bank = balance(ledger, "bets")
    stake = round(min(KELLY_FRACTION * kelly, MAX_BET_SHARE) * bank, 2)
    bet = {"id": uuid.uuid4().hex[:10], "strategy": strategy, "sport": sport, "event": event, "market": market,
           "selection": selection, "odds": odds, "probability": probability, "ev": round(edge, 4),
           "stake": stake, "bookmaker": bookmaker, "fair_odds": fair_odds, "placed_at": (now or _now()).isoformat()}
    ledger["bets"].append(bet)
    return {"status": "ok", "bet": bet}


def settle_bet(ledger: Dict[str, Any], bet_id: str, won: Optional[bool], closing_odds: Optional[float] = None,
               now: Optional[datetime] = None) -> Dict[str, Any]:
    """won=None means void (stake back). CLV: how much better our odds were than the closing line."""
    bet = next((b for b in ledger["bets"] if b["id"] == bet_id), None)
    if bet is None:
        return {"status": "error", "error": "no_such_open_bet"}
    pnl = 0.0 if won is None else (bet["stake"] * (bet["odds"] - 1) if won else -bet["stake"])
    clv = round(bet["odds"] / closing_odds - 1, 4) if closing_odds and closing_odds > 1 else None
    settled = {**bet, "won": won, "pnl": round(pnl, 2), "closing_odds": closing_odds, "clv": clv,
               "closed_at": (now or _now()).isoformat()}
    ledger["bets"] = [b for b in ledger["bets"] if b["id"] != bet_id]
    ledger["settled"].append(settled)
    return {"status": "ok", "bet": settled}


# ── the tournament ────────────────────────────────────────────────────────────────────────


def _drawdown(pnls: List[float], start: float) -> float:
    equity, peak, worst = start, start, 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        worst = max(worst, (peak - equity) / peak if peak > 0 else 0.0)
    return round(worst, 4)


def stats(ledger: Dict[str, Any]) -> Dict[str, Any]:
    """Per account and per strategy, from the ledger only."""
    out: Dict[str, Any] = {"accounts": {}, "strategies": {}}
    for account in ACCOUNTS:
        out["accounts"][account] = {"balance": round(balance(ledger, account), 2), "currency": ACCOUNTS[account]["currency"],
                                    "start": ACCOUNTS[account]["start"], "frozen": frozen(ledger, account)}
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for row in ledger["closed"] + ledger["settled"]:
        groups.setdefault(row["strategy"], []).append(row)
    for strategy, rows in groups.items():
        rows.sort(key=lambda r: r["closed_at"])
        wins = [r["pnl"] for r in rows if r["pnl"] > 0]
        losses = [-r["pnl"] for r in rows if r["pnl"] < 0]
        rs = [r["r"] for r in rows if "r" in r]
        clvs = [r["clv"] for r in rows if r.get("clv") is not None]
        account = rows[0].get("account", "bets")
        out["strategies"][strategy] = {
            "count": len(rows), "win_rate": round(len(wins) / len(rows), 3),
            "profit_factor": round(sum(wins) / sum(losses), 3) if losses else None,
            "expectancy_r": round(sum(rs) / len(rs), 3) if rs else None,
            "pnl": round(sum(r["pnl"] for r in rows), 2),
            "max_drawdown": _drawdown([r["pnl"] for r in rows], ACCOUNTS[account]["start"]),
            "avg_clv": round(sum(clvs) / len(clvs), 4) if clvs else None,
        }
    out["open_trades"], out["open_bets"] = len(ledger["open"]), len(ledger["bets"])
    return out


# ── one writer at a time, and the tools Sam calls ─────────────────────────────────────────


LOCK = threading.Lock()


def transact(change: Any) -> Any:
    """Load, change, save under one lock: the schedule and Sam's own calls never overwrite each other."""
    with LOCK:
        ledger = load()
        result = change(ledger)
        save(ledger)
        return result


def _num(args: Dict[str, Any], name: str) -> float:
    return float(args.get(name) or 0)


def trade_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """paper_trade: action open | close | status. Sam's discretionary and fundamental trades join the tournament."""
    action = str(args.get("action") or "status")
    if action == "status":
        return transact(lambda ledger: {"status": "ok", **stats(ledger), "open": ledger["open"][-20:]})
    if action == "open":
        return transact(lambda ledger: open_trade(
            ledger, account=str(args.get("account", "")), strategy=str(args.get("strategy") or "sam_discretionary"),
            source=str(args.get("source", "")), symbol=str(args.get("symbol", "")), side=str(args.get("side", "")),
            entry=_num(args, "entry"), stop=_num(args, "stop"), target=_num(args, "target"),
            risk=_num(args, "risk") or 0.01, timeframe=str(args.get("timeframe", "")), reason=str(args.get("reason", ""))))
    if action == "close":
        return transact(lambda ledger: close_trade(ledger, str(args.get("id", "")), _num(args, "price"), "sam"))
    return {"status": "error", "error": "unknown_action", "available_actions": ["close", "open", "status"]}


def bet_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    """paper_bet: action place | settle | status."""
    action = str(args.get("action") or "status")
    if action == "status":
        return transact(lambda ledger: {"status": "ok", **stats(ledger), "open_bets": ledger["bets"][-20:]})
    if action == "place":
        return transact(lambda ledger: place_bet(
            ledger, strategy=str(args.get("strategy") or "sam_bets"), sport=str(args.get("sport", "")),
            event=str(args.get("event", "")), market=str(args.get("market", "")), selection=str(args.get("selection", "")),
            odds=_num(args, "odds"), probability=_num(args, "probability"), bookmaker=str(args.get("bookmaker", "")),
            fair_odds=_num(args, "fair_odds") or None))
    if action == "settle":
        won = args.get("won")
        return transact(lambda ledger: settle_bet(ledger, str(args.get("id", "")), None if won is None else bool(won),
                                                  _num(args, "closing_odds") or None))
    return {"status": "error", "error": "unknown_action", "available_actions": ["place", "settle", "status"]}
