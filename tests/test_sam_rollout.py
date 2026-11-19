"""Sam on Hermes with market data and the code sandbox (19.11.2026)."""

from __future__ import annotations

import asyncio
import base64
import json

import httpx

from src import agent_folders, code_sandbox, hermes_gateway, hermes_tools, market_data


def test_sam_gets_research_data_and_maths_but_nothing_that_trades():
    granted = set(hermes_tools.granted("sam"))
    assert {"market_data", "run_python", "web_search", "note_write", "table_save"} <= granted
    assert "drive_save" not in granted and "food_lookup" not in granted
    assert hermes_gateway.AGENT_ACTIONS["sam"] == ("evaluate_setup", "portfolio_risk")  # no trade_decision
    assert hermes_tools.NOTE_DIRS["sam"] == "Сем"
    assert hermes_tools.AGENT_LIMITS["sam"]["market_data"] > hermes_tools.DAILY_LIMITS["market_data"]


def test_a_per_agent_limit_overrides_the_common_one(tmp_path):
    limit = hermes_tools.DailyLimit(tmp_path / "use.json", {"web_search": 1})
    assert limit.take("trainer", "web_search") and not limit.take("trainer", "web_search")
    assert all(limit.take("sam", "web_search") for _ in range(5))  # Sam's own cap is 80


def test_market_data_keeps_the_series_as_a_dataset_and_refuses_unknowns(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path))
    rows = [[1_700_000_000_000 + i * 3_600_000, 100 + i, 101 + i, 99 + i, 100.5 + i, 10] for i in range(30)]
    monkeypatch.setattr(market_data, "_crypto", lambda source, symbol, tf, limit: rows[-limit:])
    got = asyncio.run(market_data.candles("binance", "BTC/USDT", "1h", 20))
    assert got["status"] == "ok" and got["rows"] == 20 and got["dataset"] == "binance_BTC-USDT_1h"
    assert (tmp_path / "market_data" / "binance_BTC-USDT_1h.csv").read_text().count("\n") == 21
    assert len(got["preview"]) == market_data.PREVIEW_ROWS + 1
    assert asyncio.run(market_data.candles("mt5", "EURUSD", "1h"))["error"] == "unknown_source"
    assert asyncio.run(market_data.candles("yahoo", "SPY", "2h"))["error"] == "unknown_timeframe"

    def down(*_args):
        raise TimeoutError("exchange down")

    monkeypatch.setattr(market_data, "_crypto", down)
    assert asyncio.run(market_data.candles("binance", "BTC/USDT"))["status"] == "unavailable"  # never guessed


def test_run_python_sends_datasets_and_saves_charts_into_the_own_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    (code_sandbox.dataset_dir() / "binance_BTC-USDT_1h.csv").write_text("time_utc,close\nx,1\n", encoding="utf-8")
    sent = {}

    def answer(request):
        sent.update(json.loads(request.content))
        return httpx.Response(200, json={"status": "ok", "stdout": "mean=1", "stderr": "",
                                         "files": {"chart.png": base64.b64encode(b"PNG").decode()}})

    vault = tmp_path / "vault"
    result = asyncio.run(code_sandbox.run("print('mean=1')", ["binance_BTC-USDT_1h", "nope"], save_to=vault / "Сем/Таблиці",
                                          vault_root=vault, transport=httpx.MockTransport(answer)))
    assert "binance_BTC-USDT_1h.csv" in sent["files"] and result["datasets_missing"] == ["nope"]
    assert result["saved"] == ["Сем/Таблиці/chart.png"] and (vault / "Сем/Таблиці/chart.png").read_bytes() == b"PNG"
    down = httpx.MockTransport(lambda request: httpx.Response(503))
    assert asyncio.run(code_sandbox.run("1", transport=down))["status"] == "unavailable"


def test_sams_folder_has_its_map_and_andriis_rules_as_protected_notes(tmp_path):
    created = agent_folders.ensure("sam", tmp_path)
    assert "Сем/Журнал/Паперовий" in created and (tmp_path / "Сем/Карта.md").is_file()
    risk = (tmp_path / "Сем/База/SAM_RISK_BLOCKS.md").read_text(encoding="utf-8")
    assert risk.startswith("---\nandrii_protected: true") and "Hard SL" in risk
    assert agent_folders.ensure("sam", tmp_path) == []
