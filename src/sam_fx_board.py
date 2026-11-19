"""Read a fresh FX board produced by Sam's local IBKR Paper market-data bridge."""
import json
import math
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.data_paths import data_dir

FILE = "ibkr-paper-fx.json"
MAX_AGE = 15


def session_windows(now):
    """Indicative FX dealing hours, in venue local time; holidays may differ."""
    sessions = []
    for zone, start in (("Asia/Tokyo", 9), ("Europe/London", 8), ("America/New_York", 8), ("Australia/Sydney", 8)):
        try:
            local = datetime.fromtimestamp(now, timezone.utc).astimezone(ZoneInfo(zone))
        except ZoneInfoNotFoundError:
            continue
        if local.weekday() < 5 and start <= local.hour < start + 9:
            sessions.append(zone)
    return sessions


def snapshot(now=None):
    current = time.time() if now is None else now
    try:
        path = data_dir("market_data") / FILE
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["provider"] != "IBKR Paper" or not 0 <= current - data["written_at"] <= MAX_AGE:
            raise ValueError("stale_snapshot")
        rows = [r for r in data["quotes"] if fresh(r, current)]
    except (OSError, ValueError, TypeError, KeyError):
        return {"status": "unavailable", "source": "ibkr_fx", "reason": "missing_or_stale_snapshot"}
    if not rows:
        return {"status": "unavailable", "source": "ibkr_fx", "reason": "no_fresh_live_bid_ask"}
    return {"status": "ok", "source": "ibkr_fx", "clock": "local_receipt_utc_epoch",
            "session_windows": session_windows(current), "written_at": data["written_at"],
            "requested_pairs": data["requested_pairs"], "quotes": rows}


def fresh(row, now):
    return (row["data_type"] == 1 and all(math.isfinite(row[k]) for k in ("bid", "ask"))
            and 0 < row["bid"] <= row["ask"]
            and all(0 <= now - row[k] <= MAX_AGE for k in ("bid_received", "ask_received")))
