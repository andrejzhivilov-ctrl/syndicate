"""Durable paper-only tracker; atomic exposure limits and single settlement."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

from src.agents.director_base import DirectorStore, text, utc_now


def anti_tilt(records: list[dict]) -> dict:
    settled = sorted((r for r in records if r["state"] == "settled"), key=lambda r: r["settled_at"])
    streak = []
    blocked_until = None
    for record in settled:
        when = datetime.fromisoformat(record["settled_at"])
        if record["outcome"] == "void":
            continue
        if record["outcome"] != "loss":
            streak = []
            continue
        streak = [t for t in streak if t.date() == when.date()] + [when]
        if len(streak) >= 3:
            blocked_until = when + timedelta(hours=24)
    active = blocked_until is not None and utc_now() < blocked_until
    return {"blocked": active, "blocked_until": blocked_until.isoformat() if active else None}


def record_paper(store: DirectorStore, payload: dict, signal: dict) -> dict:
    event_id = text(payload["event_id"], "event_id", 200)
    selection = text(payload["selection"], "selection", 200)
    market = text(payload["market"], "market", 200)
    db = store.connect()
    try:
        db.execute("BEGIN IMMEDIATE")
        rows = db.execute("SELECT payload FROM records WHERE kind='paper'").fetchall()
        records = [json.loads(row["payload"]) for row in rows]
        if anti_tilt(records)["blocked"]:
            raise ValueError("anti_tilt_active")
        identity = (event_id, market, selection)
        if any((r["event_id"], r["market"], r["selection"]) == identity for r in records):
            raise ValueError("duplicate_selection")
        open_event = sum(r["stake"] for r in records if r["event_id"] == event_id and r["state"] == "open")
        if open_event + signal["stake"] > signal["bankroll"] * signal["event_risk_cap"] + 1e-8:
            raise ValueError("event_exposure_limit")
        record = {"id": uuid.uuid4().hex, "created_at": utc_now().isoformat(), "event_id": event_id,
                  "selection": selection, "market": market, "state": "open", "mode": "paper",
                  "stake": signal["stake"], "odds": signal["decimal_odds"], "signal": signal}
        db.execute("INSERT INTO records VALUES (?, 'paper', ?, ?)",
                   (record["id"], record["created_at"], json.dumps(record, allow_nan=False)))
        db.commit()
        return record
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def settle(store: DirectorStore, payload: dict) -> dict:
    outcome = payload["outcome"]
    if outcome not in {"win", "loss", "void"}:
        raise ValueError("invalid_outcome")
    record_id = text(payload["record_id"], "record_id", 32)
    records = store.list("paper")
    record = next((r for r in records if r["id"] == record_id), None)
    if record is None:
        raise ValueError("unknown_record")
    pnl = {"win": record["stake"] * (record["odds"] - 1), "loss": -record["stake"], "void": 0}[outcome]
    return store.transition(record_id, "paper", "open", {"state": "settled", "outcome": outcome,
                            "pnl": round(pnl, 2), "settled_at": utc_now().isoformat()})


def report(store: DirectorStore) -> dict:
    records = store.list("paper")
    settled = [r for r in records if r["state"] == "settled" and r["outcome"] != "void"]
    turnover = sum(r["stake"] for r in settled)
    pnl = sum(r["pnl"] for r in settled)
    return {"status": "ok", "mode": "paper", "recorded": len(records), "settled": len(settled),
            "pnl": round(pnl, 2), "roi": pnl / turnover if turnover else None,
            "win_rate": sum(r["outcome"] == "win" for r in settled) / len(settled) if settled else None,
            "audit_target": 1000, "sample_complete": len(settled) >= 1000, "anti_tilt": anti_tilt(records)}
