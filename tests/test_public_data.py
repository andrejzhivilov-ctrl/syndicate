"""Free public sources: real values or an honest reason, never a made-up number."""
from __future__ import annotations

import asyncio

import httpx

from src.agent_chat import pool_command
from src.integrations.public_data import air_alerts, nbu_rates, source_reply, weather


def _transport(routes):
    def handler(request: httpx.Request) -> httpx.Response:
        for host, response in routes.items():
            if request.url.host == host:
                return response(request) if callable(response) else response
        return httpx.Response(404)
    return httpx.MockTransport(handler)


NBU = httpx.Response(200, json=[{"cc": "USD", "rate": 45.5923, "exchangedate": "29.10.2026"},
                                {"cc": "EUR", "rate": 50.7666, "exchangedate": "29.10.2026"},
                                {"cc": "PLN", "rate": 11.1, "exchangedate": "29.10.2026"}])
METEO = httpx.Response(200, json={
    "current": {"temperature_2m": 7.3, "apparent_temperature": 5.7, "pressure_msl": 1024.0, "cloud_cover": 94,
                "visibility": 28300.0, "wind_speed_10m": 0.76, "wind_gusts_10m": 2.4},
    "hourly": {"time": ["t0", "t1"], "wind_speed_925hPa": [3.1, None], "wind_speed_10m": [1.0, 2.0]},
})


class _Vault:
    def __init__(self, secrets):
        self.secrets = secrets

    async def get_secret(self, path):
        return self.secrets.get(path, {})


def test_nbu_rates_are_parsed_and_failures_are_unavailable():
    data = asyncio.run(nbu_rates(transport=_transport({"bank.gov.ua": NBU})))
    assert data == {"status": "ok", "source": "bank.gov.ua", "date": "29.10.2026",
                    "rates": {"USD": 45.5923, "EUR": 50.7666}}
    down = asyncio.run(nbu_rates(transport=_transport({"bank.gov.ua": httpx.Response(503)})))
    assert down["status"] == "unavailable" and down["reason"] == "http_503"


def test_weather_keeps_missing_fields_as_none():
    data = asyncio.run(weather(50.45, 30.52, transport=_transport({"api.open-meteo.com": METEO})))
    assert data["status"] == "ok" and data["current"]["temperature_2m"] == 7.3
    assert data["hours"][1]["wind_speed_925hPa"] is None and data["hours"][0]["cloud_cover_low"] is None


def test_alerts_need_a_token_and_never_invent_calm():
    assert asyncio.run(air_alerts(None))["reason"] == "token_not_configured"
    seen = []

    def alerts(request):
        seen.append(request.headers["Authorization"])
        return httpx.Response(200, json={"alerts": [{"location_title": "Київ", "location_oblast": "м. Київ",
                                                     "alert_type": "air_raid", "started_at": "2026-10-29T03:00"}]})

    data = asyncio.run(air_alerts("tok", transport=_transport({"api.alerts.in.ua": alerts})))
    assert data["alerts"][0]["oblast"] == "м. Київ" and seen == ["Bearer tok"]
    broken = asyncio.run(air_alerts("tok", transport=_transport({"api.alerts.in.ua": httpx.Response(401)})))
    assert broken["status"] == "unavailable"


def test_bot_commands_answer_without_a_model():
    assert pool_command({"text": "/rates"}) == ("/rates", "")
    vault = _Vault({})
    rates = asyncio.run(source_reply("/rates", vault, transport=_transport({"bank.gov.ua": NBU})))
    assert "USD: 45.5923 грн" in rates["response"]
    no_point = asyncio.run(source_reply("/weather", vault))
    assert no_point["reason"] == "location_not_set"
    point = _Vault({"secret/data/syndicate/agents/eva/briefing": {"latitude": 50.45, "longitude": 30.52,
                                                                   "label": "Київ"}})
    ok = asyncio.run(source_reply("/weather", point, transport=_transport({"api.open-meteo.com": METEO})))
    assert "Київ" in ok["response"] and "7.3°C" in ok["response"] and "немає даних" in ok["response"]
    assert "Токен alerts.in.ua ще не внесено" in asyncio.run(source_reply("/alerts", vault))["response"]
