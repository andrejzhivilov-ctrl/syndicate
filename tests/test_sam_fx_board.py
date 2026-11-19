import json
from collections import deque

import pytest

from src.sam_fx_board import FILE, snapshot
from tools.sam_fx_bridge import PAIRS, metrics


def test_snapshot_requires_live_both_sides(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    path = tmp_path / "market_data" / FILE
    path.parent.mkdir()
    assert snapshot(100)["status"] == "unavailable"
    row = {"data_type": 1, "bid": 1.1, "ask": 1.11, "bid_received": 95, "ask_received": 99}
    def write():
        path.write_text(json.dumps({"provider": "IBKR Paper", "written_at": 100, "requested_pairs": 28,
                                    "quotes": [row]}), encoding="utf-8")
    write()
    assert snapshot(100)["quotes"] == [row]
    assert snapshot(116)["status"] == "unavailable"
    row["data_type"] = 3
    write()
    assert snapshot(100)["status"] == "unavailable"
    row.update(data_type=1, ask_received=10)
    write()
    assert snapshot(100)["status"] == "unavailable"


def test_rank_warmup_and_gaps():
    points = deque(maxlen=16)
    for i in range(16):
        value = metrics({"bid": 1 + i / 1000, "ask": 1.001 + i / 1000}, points, 60*i)
        if i < 15:
            assert value["volatility_15m_bp"] is None
    assert value["volatility_15m_bp"] > 0
    assert metrics({"bid": 1., "ask": 1.001}, points, 1200)["volatility_15m_bp"] is None
    assert len(set(PAIRS)) == 45
    assert metrics({"bid": 1., "ask": 1.}, deque(), 0)["spread_bp"] == pytest.approx(0)
