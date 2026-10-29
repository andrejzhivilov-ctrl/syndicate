"""Free official sources for Sam: CFTC COT, FRED, EIA, SEC EDGAR.

* CFTC Commitments of Traders (publicreporting.cftc.gov, legacy futures-only) — no key.
* FRED (St. Louis Fed): real yields, DXY proxies, CPI — free key ``fred_api_key``.
* EIA: weekly crude/gas inventories — free key ``eia_api_key``.
* SEC EDGAR: company filings (10-K, 10-Q, 8-K) — no key, but the SEC requires a
  User-Agent naming a contact (``sec_user_agent`` in Vault ``api-keys``).

Every function returns real fetched values or ``unavailable`` with a reason.
Missing observations stay ``None`` (FRED marks them "."), never 0.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
import structlog

from src.vault_paths import secret_path

logger = structlog.get_logger(__name__)

COT_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
EIA_URL = "https://api.eia.gov/v2/{route}/data/"
EDGAR_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
TIMEOUT_S = 20
FILING_FORMS = frozenset({"10-K", "10-Q", "8-K", "20-F", "6-K"})


def _unavailable(source: str, reason: str) -> Dict[str, Any]:
    return {"status": "unavailable", "source": source, "reason": reason}


async def _get_json(source: str, url: str, *, params: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None, transport: Any = None) -> Any:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S, transport=transport, follow_redirects=False) as client:
            response = await client.get(url, params=params, headers=headers)
    except Exception as exc:  # noqa: BLE001 - never log URLs: FRED/EIA keys travel in the query
        logger.warning("macro_source_error", source=source, error_type=type(exc).__name__)
        return _unavailable(source, "network_error")
    if response.status_code != 200:
        return _unavailable(source, f"http_{response.status_code}")
    try:
        return response.json()
    except ValueError:
        return _unavailable(source, "invalid_json")


def _int(value: Any) -> Optional[int]:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


async def cot_positioning(market_code: str, *, transport: Any = None) -> Dict[str, Any]:
    """Latest COT report for one CFTC contract market code (e.g. 088691 gold)."""
    if not market_code.isalnum():
        return _unavailable("cftc.gov", "invalid_market_code")
    data = await _get_json("cftc.gov", COT_URL, transport=transport, params={
        "$limit": 1, "$order": "report_date_as_yyyy_mm_dd DESC", "cftc_contract_market_code": market_code})
    if isinstance(data, dict) and data.get("status") == "unavailable":
        return data
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        return _unavailable("cftc.gov", "no_report")
    row = data[0]
    long_nc, short_nc = _int(row.get("noncomm_positions_long_all")), _int(row.get("noncomm_positions_short_all"))
    long_c, short_c = _int(row.get("comm_positions_long_all")), _int(row.get("comm_positions_short_all"))
    return {"status": "ok", "source": "cftc.gov", "market": row.get("market_and_exchange_names"),
            "report_date": str(row.get("report_date_as_yyyy_mm_dd") or "")[:10] or None,
            "open_interest": _int(row.get("open_interest_all")),
            "noncommercial_net": None if None in (long_nc, short_nc) else long_nc - short_nc,
            "commercial_net": None if None in (long_c, short_c) else long_c - short_c}


async def fred_latest(series_id: str, api_key: Optional[str], *, transport: Any = None) -> Dict[str, Any]:
    if not api_key:
        return _unavailable("fred", "key_not_configured")
    data = await _get_json("fred", FRED_URL, transport=transport, params={
        "series_id": series_id, "api_key": api_key, "file_type": "json", "sort_order": "desc", "limit": 1})
    if isinstance(data, dict) and data.get("status") == "unavailable":
        return data
    obs = data.get("observations") if isinstance(data, dict) else None
    if not isinstance(obs, list) or not obs or not isinstance(obs[0], dict):
        return _unavailable("fred", "no_observation")
    raw = obs[0].get("value")
    try:
        value = None if raw in (None, ".") else float(raw)
    except (TypeError, ValueError):
        value = None
    return {"status": "ok", "source": "fred", "series": series_id, "date": obs[0].get("date"), "value": value}


async def eia_latest(route: str, series: str, api_key: Optional[str], *, transport: Any = None) -> Dict[str, Any]:
    """Latest weekly value, e.g. route ``petroleum/stoc/wstk``, series ``WCESTUS1`` (US crude stocks)."""
    if not api_key:
        return _unavailable("eia", "key_not_configured")
    if not all(part.isalnum() for part in route.split("/")) or not series.isalnum():
        return _unavailable("eia", "invalid_route_or_series")
    data = await _get_json("eia", EIA_URL.format(route=route), transport=transport, params={
        "api_key": api_key, "frequency": "weekly", "data[0]": "value", "facets[series][]": series,
        "sort[0][column]": "period", "sort[0][direction]": "desc", "length": 1})
    if isinstance(data, dict) and data.get("status") == "unavailable":
        return data
    response = data.get("response") if isinstance(data, dict) else None
    rows = response.get("data") if isinstance(response, dict) else None
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        return _unavailable("eia", "no_observation")
    try:
        value = float(rows[0].get("value"))
    except (TypeError, ValueError):
        value = None
    return {"status": "ok", "source": "eia", "series": series, "period": rows[0].get("period"),
            "value": value, "units": rows[0].get("units")}


async def edgar_filings(cik: int, user_agent: Optional[str], *, limit: int = 5,
                        transport: Any = None) -> Dict[str, Any]:
    """Latest material filings (10-K, 10-Q, 8-K, 20-F, 6-K) of one company."""
    if not user_agent or "@" not in user_agent:
        return _unavailable("sec.gov", "user_agent_not_configured")
    data = await _get_json("sec.gov", EDGAR_URL.format(cik=int(cik)), transport=transport,
                           headers={"User-Agent": user_agent})
    if isinstance(data, dict) and data.get("status") == "unavailable":
        return data
    filings_block = data.get("filings") if isinstance(data, dict) else None
    recent = filings_block.get("recent") if isinstance(filings_block, dict) else None
    if not isinstance(recent, dict):
        return _unavailable("sec.gov", "no_filings")
    forms, dates, numbers = (recent.get(k) for k in ("form", "filingDate", "accessionNumber"))
    if not all(isinstance(x, list) for x in (forms, dates, numbers)) or not len(forms) == len(dates) == len(numbers):
        return _unavailable("sec.gov", "inconsistent_filings")  # never pair a form with another filing's date
    filings: List[Dict[str, Any]] = [
        {"form": f, "date": d, "accession": n}
        for f, d, n in zip(forms, dates, numbers, strict=True) if f in FILING_FORMS
    ][:limit]
    return {"status": "ok", "source": "sec.gov", "company": data.get("name"), "filings": filings}


async def macro_keys(vault: Any) -> Dict[str, Optional[str]]:
    try:
        keys = await vault.get_secret(secret_path("api-keys")) or {}
    except Exception:  # noqa: BLE001 - no keys means every keyed source reports unavailable
        keys = {}
    return {k: (keys.get(k) if isinstance(keys.get(k), str) and keys.get(k) else None)
            for k in ("fred_api_key", "eia_api_key", "sec_user_agent")}
