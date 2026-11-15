"""Power outage group (черга) by street and house, through Alice (14.11.2026).

Only Yasno (DTEK) publishes an address lookup without a key or a bot check:
``app.yasno.ua/api/blackout-service/public/shutdowns/addresses/v2`` (checked live 14.11.2026).
It covers Kyiv (DTEK Kyiv grids) and Dnipropetrovsk oblast, where two networks serve
customers: DnEM and CEK, each with its own schedule. Other oblenergos show the group only
on their own sites; for them Alice says so instead of guessing.

There is no list of groups by district anywhere open, so Alice shows the groups of the
houses of one street instead (at most ``MAX_HOUSES`` lookups per request).
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
import structlog

logger = structlog.get_logger(__name__)

API = "https://app.yasno.ua/api/blackout-service/public/shutdowns/addresses/v2"
ICON = "💡"
MAX_HOUSES = 40
MAX_CHOICES = 10
PAUSE_S = 0.2  # between house lookups, so one street is not a burst
#: power source key -> (Yasno region id, networks as (dso id, power source key, label), has cities).
REGIONS: Dict[str, Tuple[int, Tuple[Tuple[int, str, str], ...], bool]] = {
    "kyiv": (25, ((902, "kyiv", "ДТЕК Київські електромережі"),), False),
    "dnipro": (3, ((301, "dnipro", "ДнЕМ"), (303, "dnipro-cek", "ЦЕК")), True),
    "dnipro-cek": (3, ((301, "dnipro", "ДнЕМ"), (303, "dnipro-cek", "ЦЕК")), True),
}
_PREFIX = re.compile(r"^(вул\.?|вулиця|просп\.?|проспект|пров\.?|провулок|бульв\.?|бульвар|пл\.?|площа|"
                     r"м\.|смт\.?|с\.|село|місто)\s+", re.IGNORECASE)


def _plain(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("’", "'").replace("ʼ", "'")).strip()


def _bare(name: str) -> str:
    """A street or town name without «вул.», «м.» and the like."""
    return _PREFIX.sub("", _plain(name))


async def _get(path: str, params: Dict[str, Any], transport: Any = None) -> Optional[Any]:
    try:
        async with httpx.AsyncClient(timeout=20, transport=transport) as client:
            response = await client.get(f"{API}/{path}", params=params)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("power_address_failed", path=path, error_type=type(exc).__name__)
        return None


def _items(data: Any) -> List[Tuple[int, str]]:
    return [(int(item["id"]), str(item["value"])) for item in data or []
            if isinstance(item, dict) and str(item.get("id", "")).isdigit() and item.get("value")]


def pick(items: List[Tuple[int, str]], wanted: str) -> List[Tuple[int, str]]:
    """Exact names first (without «вул.»/«м.»), then those containing every word Andrii typed."""
    target = _bare(wanted)
    exact = [item for item in items if _bare(item[1]) == target]
    if exact:
        return exact
    words = target.split()
    return [item for item in items if all(word in _plain(item[1]) for word in words)]


def split_address(text: str) -> Tuple[str, str, str]:
    """(town, street, house) from «Дніпро, вул. Гоголя 5», «Гоголя 5» or «Гоголя»."""
    town, _, rest = text.rpartition(",") if "," in text else ("", "", text)
    words = rest.split()
    house = words.pop() if len(words) > 1 and any(ch.isdigit() for ch in words[-1]) else ""
    return town.strip(), " ".join(words).strip(), house


async def _city(region: int, dso: int, town: str, transport: Any) -> Optional[int]:
    query = _bare(town).split()[0] if _bare(town) else ""
    if not query:
        return None
    found = pick(_items(await _get("cities", {"regionId": region, "dsoId": dso, "query": query}, transport)), town)
    cities = [item for item in found if item[1].startswith("м. ")] or found
    return cities[0][0] if cities else None


async def streets(source: str, town: str, street: str, transport: Any = None) -> List[Dict[str, Any]]:
    """Matching streets in every network of the region: dso, network label, power source, ids, name."""
    region, networks, has_cities = REGIONS[source]
    query = max(_bare(street).split(), key=len, default="")
    out: List[Dict[str, Any]] = []
    for dso, power_source, label in networks:
        params: Dict[str, Any] = {"regionId": region, "dsoId": dso, "query": query[:40]}
        if has_cities:
            city = await _city(region, dso, town, transport)
            if city is None:
                continue
            params["cityId"] = city
        for street_id, name in pick(_items(await _get("streets", params, transport)), street):
            out.append({"dso": dso, "label": label, "source": power_source, "region": region,
                        "city": params.get("cityId"), "street": street_id, "name": name})
    return out


async def group_of(found: Dict[str, Any], house_id: int, transport: Any = None) -> Optional[str]:
    params = {"regionId": found["region"], "dsoId": found["dso"], "streetId": found["street"], "houseId": house_id}
    if found["city"] is not None:
        params["cityId"] = found["city"]
    data = await _get("group", params, transport)
    if not isinstance(data, dict) or data.get("group") is None:
        return None
    return f"{data['group']}.{data['subgroup']}" if data.get("subgroup") is not None else str(data["group"])


async def houses(found: Dict[str, Any], transport: Any = None) -> List[Tuple[int, str]]:
    return _items(await _get("houses", {"regionId": found["region"], "dsoId": found["dso"],
                                        "streetId": found["street"]}, transport))


def _choose_cmd(found: Dict[str, Any], town: str, group: str) -> str:
    network = "ЦЕК " if found["source"] == "dnipro-cek" else ""
    return f"/svitlo {network}{town or 'Київ'} {group}"


async def _one_house(found: Dict[str, Any], town: str, house: str, transport: Any) -> str:
    listed = await houses(found, transport)
    match = [item for item in listed if _plain(item[1]) == _plain(house)]
    if not match:
        sample = ", ".join(value for _id, value in listed[:30])
        return f"Будинку {house} на «{found['name']}» у мережі {found['label']} немає. Є: {sample or 'нічого'}"
    group = await group_of(found, match[0][0], transport)
    if group is None:
        return f"{found['name']} {house}: черга зараз недоступна, спробуй пізніше."
    return (f"{found['name']} {house} — черга {group} (мережа {found['label']}).\n"
            f"Вибрати: {_choose_cmd(found, town, group)}")


async def street_groups(found: Dict[str, Any], transport: Any = None) -> Dict[str, List[str]]:
    """group -> house numbers of one street, at most MAX_HOUSES lookups."""
    out: Dict[str, List[str]] = {}
    for index, (house_id, value) in enumerate((await houses(found, transport))[:MAX_HOUSES]):
        if index:
            await asyncio.sleep(PAUSE_S)
        group = await group_of(found, house_id, transport)
        out.setdefault(group or "невідомо", []).append(value)
    return out


async def _whole_street(found: Dict[str, Any], town: str, transport: Any) -> str:
    groups = await street_groups(found, transport)
    if not groups:
        return f"На «{found['name']}» у мережі {found['label']} будинків не знайшов."
    lines = [f"{found['name']} (мережа {found['label']}), черги за будинками:"]
    lines += [f"• {group}: {', '.join(values)}" for group, values in sorted(groups.items())]
    lines.append(f"Вибрати: {_choose_cmd(found, town, '<черга>')}")
    return "\n".join(lines)


def unsupported(source: Optional[str], oblast: str) -> str:
    where = f"для «{oblast}»" if oblast else "тут"
    return (f"{ICON} Черга за адресою {where} відкрито ніде не публікується. Її показує сайт обленерго "
            "або рахунок; пошук за вулицею є для м. Києва й Дніпропетровської області.")


async def lookup(source: Optional[str], saved_town: str, text: str, transport: Any = None) -> Dict[str, Any]:
    """``/svitlo адреса [Місто,] вулиця [будинок]``: the group of a house, or of every house of a street."""
    if source not in REGIONS:
        return {"status": "unavailable", "reply": unsupported(source, "")}
    town, street, house = split_address(text)
    town = town or saved_town
    if not street:
        return {"status": "completed", "reply": f"{ICON} Напиши вулицю: /svitlo адреса Дніпро, Гоголя 5"}
    if REGIONS[source][2] and not town:
        return {"status": "completed", "reply": f"{ICON} Напиши й місто: /svitlo адреса Дніпро, {street} {house}".strip()}
    found = await streets(source, town, street, transport)
    if not found:
        return {"status": "completed", "reply": f"{ICON} Вулицю «{street}» {('у ' + town) if town else ''} не знайшов."}
    if len(found) > 1 and len({item["name"] for item in found}) > 1:
        names = "\n".join(f"• {item['name']} ({item['label']})" for item in found[:MAX_CHOICES])
        return {"status": "completed", "reply": f"{ICON} Кілька вулиць, уточни назву:\n{names}"}
    parts = [await (_one_house(item, town, house, transport) if house else _whole_street(item, town, transport))
             for item in found]
    return {"status": "completed", "reply": f"{ICON} " + "\n\n".join(parts)}
