"""Free public sources for Fin and Eva's briefings: NBU rates, Open-Meteo, alerts.in.ua.

Every function returns ``{"status": "ok", ...}`` with real fetched values or an
honest ``unavailable`` with a reason. Nothing is cached as if it were fresh and
nothing is filled in when a field is missing (it stays ``None``).

* NBU (bank.gov.ua) and Open-Meteo need no key.
* Weather needs a location the operator sets once (Vault ``agents/eva/briefing``:
  latitude, longitude, label). Eva's GPS stays off: this is a fixed point.
* alerts.in.ua needs a free token (Vault ``api-keys`` → ``alerts_in_ua_token``).
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import httpx
import structlog

from src.vault_paths import agent_secret_path, secret_path

logger = structlog.get_logger(__name__)

NBU_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"
METEO_URL = "https://api.open-meteo.com/v1/forecast"
ALERTS_URL = "https://api.alerts.in.ua/v1/alerts/active.json"
TIMEOUT_S = 15
FORECAST_HOURS = 24
#: Pressure levels ≈ heights above sea level: 925 hPa ~ 750 m, 850 hPa ~ 1500 m, 800 hPa ~ 2000 m.
_HOURLY = ("temperature_2m", "cloud_cover_low", "visibility", "precipitation_probability", "wind_speed_10m",
           "wind_gusts_10m", "wind_speed_925hPa", "wind_speed_850hPa", "wind_speed_800hPa")
_CURRENT = ("temperature_2m", "apparent_temperature", "pressure_msl", "cloud_cover", "visibility",
            "wind_speed_10m", "wind_gusts_10m")


def _unavailable(source: str, reason: str) -> Dict[str, Any]:
    return {"status": "unavailable", "source": source, "reason": reason}


async def _get(url: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
               transport: Any = None) -> httpx.Response:
    async with httpx.AsyncClient(timeout=TIMEOUT_S, transport=transport, follow_redirects=False) as client:
        return await client.get(url, params=params, headers=headers)


async def nbu_rates(codes: Iterable[str] = ("USD", "EUR"), *, transport: Any = None) -> Dict[str, Any]:
    """Official NBU rates for today."""
    try:
        response = await _get(NBU_URL, params={"json": ""}, transport=transport)
        rows = response.json() if response.status_code == 200 else None
    except Exception as exc:  # noqa: BLE001 - a dead source must not break a report
        logger.warning("nbu_rates_error", error_type=type(exc).__name__)
        return _unavailable("bank.gov.ua", "network_error")
    if not isinstance(rows, list):
        return _unavailable("bank.gov.ua", f"http_{response.status_code}")
    wanted = {c.upper() for c in codes}
    rates = {r["cc"]: float(r["rate"]) for r in rows if isinstance(r, dict) and r.get("cc") in wanted and r.get("rate")}
    if not rates:
        return _unavailable("bank.gov.ua", "no_rates_in_response")
    date = next((r.get("exchangedate") for r in rows if isinstance(r, dict) and r.get("cc") in rates), None)
    return {"status": "ok", "source": "bank.gov.ua", "date": date, "rates": rates}


async def weather(latitude: float, longitude: float, *, transport: Any = None) -> Dict[str, Any]:
    """Current weather and the next 24 hours, with winds aloft (m/s)."""
    params = {"latitude": latitude, "longitude": longitude, "current": ",".join(_CURRENT),
              "hourly": ",".join(_HOURLY), "wind_speed_unit": "ms", "forecast_hours": FORECAST_HOURS,
              "timezone": "Europe/Kyiv"}
    try:
        response = await _get(METEO_URL, params=params, transport=transport)
        data = response.json() if response.status_code == 200 else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("weather_error", error_type=type(exc).__name__)
        return _unavailable("open-meteo.com", "network_error")
    if not isinstance(data, dict) or not isinstance(data.get("current"), dict):
        return _unavailable("open-meteo.com", f"http_{response.status_code}")
    hourly = data.get("hourly") or {}
    hours: List[Dict[str, Any]] = [
        {"time": t, **{k: (hourly.get(k) or [None] * len(hourly.get("time", [])))[i] for k in _HOURLY}}
        for i, t in enumerate(hourly.get("time", []))
    ]
    return {"status": "ok", "source": "open-meteo.com", "current": {k: data["current"].get(k) for k in _CURRENT},
            "hours": hours}


async def air_alerts(token: Optional[str], *, transport: Any = None) -> Dict[str, Any]:
    """Active air-raid alerts by region (alerts.in.ua)."""
    if not token:
        return _unavailable("alerts.in.ua", "token_not_configured")
    try:
        response = await _get(ALERTS_URL, headers={"Authorization": f"Bearer {token}"}, transport=transport)
        data = response.json() if response.status_code == 200 else None
    except Exception as exc:  # noqa: BLE001 - never log the token
        logger.warning("air_alerts_error", error_type=type(exc).__name__)
        return _unavailable("alerts.in.ua", "network_error")
    if not isinstance(data, dict) or not isinstance(data.get("alerts"), list):
        return _unavailable("alerts.in.ua", f"http_{response.status_code}")
    alerts = [{"location": a.get("location_title"), "type": a.get("alert_type"), "since": a.get("started_at"),
               "oblast": a.get("location_oblast")} for a in data["alerts"] if isinstance(a, dict)]
    return {"status": "ok", "source": "alerts.in.ua", "alerts": alerts}


async def briefing_location(vault: Any) -> Optional[Dict[str, Any]]:
    """The fixed point the operator chose for weather (never a live GPS fix)."""
    try:
        loc = await vault.get_secret(agent_secret_path("eva", "briefing")) or {}
        return {"latitude": float(loc["latitude"]), "longitude": float(loc["longitude"]),
                "label": str(loc.get("label") or "")}
    except Exception:  # noqa: BLE001 - missing or malformed means "not set"
        return None


async def alerts_token(vault: Any) -> Optional[str]:
    try:
        token = (await vault.get_secret(secret_path("api-keys")) or {}).get("alerts_in_ua_token")
    except Exception:  # noqa: BLE001
        return None
    return token if isinstance(token, str) and token else None


def _fmt(value: Any, unit: str = "") -> str:
    return "немає даних" if value is None else f"{value}{unit}"


async def source_reply(command: str, vault: Any, *, transport: Any = None) -> Dict[str, Any]:
    """/rates, /weather, /alerts — real data or an honest reason, no model call."""
    base = {"mode": "source", "command": command}
    if command == "/rates":
        data = await nbu_rates(transport=transport)
        if data["status"] != "ok":
            return {**base, **data, "response": "НБУ зараз не відповідає, курсів немає."}
        lines = [f"Офіційний курс НБУ на {data['date']}:"] + [f"• {c}: {r:.4f} грн" for c, r in sorted(data["rates"].items())]
        return {**base, "status": "completed", "response": "\n".join(lines)}
    if command == "/weather":
        loc = await briefing_location(vault)
        if loc is None:
            return {**base, "status": "unavailable", "reason": "location_not_set",
                    "response": "Точку для погоди ще не задано (налаштовує Андрій через сховище секретів)."}
        data = await weather(loc["latitude"], loc["longitude"], transport=transport)
        if data["status"] != "ok":
            return {**base, **data, "response": "Сервіс погоди зараз не відповідає."}
        cur = data["current"]
        lines = [f"Погода{(' — ' + loc['label']) if loc['label'] else ''} (Open-Meteo):",
                 f"• {_fmt(cur['temperature_2m'], '°C')}, відчувається {_fmt(cur['apparent_temperature'], '°C')}",
                 f"• Тиск {_fmt(cur['pressure_msl'], ' гПа')}, хмарність {_fmt(cur['cloud_cover'], '%')}, "
                 f"видимість {_fmt(cur['visibility'], ' м')}",
                 f"• Вітер {_fmt(cur['wind_speed_10m'], ' м/с')}, пориви {_fmt(cur['wind_gusts_10m'], ' м/с')}"]
        if data["hours"]:
            h = data["hours"][min(3, len(data["hours"]) - 1)]
            lines.append(f"• Через 3 год вітер на ~750/1500/2000 м: {_fmt(h['wind_speed_925hPa'])}/"
                         f"{_fmt(h['wind_speed_850hPa'])}/{_fmt(h['wind_speed_800hPa'])} м/с")
        return {**base, "status": "completed", "response": "\n".join(lines)}
    if command == "/alerts":
        data = await air_alerts(await alerts_token(vault), transport=transport)
        if data["status"] != "ok":
            text = ("Токен alerts.in.ua ще не внесено." if data["reason"] == "token_not_configured"
                    else "alerts.in.ua зараз не відповідає.")
            return {**base, **data, "response": text}
        oblasts = sorted({a["oblast"] or a["location"] for a in data["alerts"] if a["oblast"] or a["location"]})
        text = ("Активних тривог немає." if not oblasts
                else f"Тривога ({len(oblasts)}): " + ", ".join(oblasts))
        return {**base, "status": "completed", "response": text + "\nДжерело: alerts.in.ua"}
    return {**base, "status": "error", "error": "unknown_command"}
