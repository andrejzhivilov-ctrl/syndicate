"""Air-raid watch: signed Ukraine Alarm webhooks -> the operator's phrases -> Alice's Telegram bot.

The API refuses the server's address, so Ukraine Alarm pushes events to
``/webhook/ukrainealarm``. Each event carries a snapshot of the region's active levels,
which replaces the stored state (``status`` alone can describe one of several causes).
Districts and communities roll up into their oblast, so all of Ukraine fits one bot; the
operator can narrow the notices to any oblast, district or community with /regions.
No model is called. An event that is unsigned, stale or repeated changes nothing.
"""
from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Mapping, Optional, Tuple

import structlog
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from src.alert_phrases import AlertTracker
from src.data_paths import ensure_dir

logger = structlog.get_logger(__name__)

ALERT_BOT = "alice"
REPLAY_WINDOW_S = 300
FLUSH_INTERVAL_S = 5
#: Notifications joined into one Telegram message, so a mass attack stays readable.
BATCH = 15
PUBLIC_KEY_PATH = Path(__file__).with_name("ukrainealarm_webhook_public.pem")
#: The tree of /api/v3/regions, region id -> [name, parent id].
_TABLE: Dict[str, List[Any]] = json.loads(
    Path(__file__).with_name("ukrainealarm_regions.json").read_text(encoding="utf-8"))["regions"]
NAMES: Dict[str, str] = {region: entry[0] for region, entry in _TABLE.items()}
UP: Dict[str, Optional[str]] = {region: entry[1] for region, entry in _TABLE.items()}
STATES: Dict[str, str] = {region: NAMES[region] for region, parent in UP.items() if parent is None}
_LEVEL_NAMES = {"R": "червоний", "Y": "жовтий", "P": "частина області"}
#: Candidates shown when a name fits several places.
MAX_CANDIDATES = 20


def _lineage(region: str) -> List[str]:
    """The region, then its district and oblast."""
    line = [region]
    while UP.get(line[-1]) is not None:
        line.append(str(UP[line[-1]]))
    return line


PARENTS: Dict[str, str] = {region: _lineage(region)[-1] for region in UP}


def state_path() -> Path:
    return ensure_dir("alerts") / "state.json"


def _public_key(pem: Optional[bytes]) -> Optional[rsa.RSAPublicKey]:
    try:
        key = serialization.load_pem_public_key(pem if pem is not None else PUBLIC_KEY_PATH.read_bytes())
    except (OSError, ValueError) as exc:
        logger.warning("ukrainealarm_public_key_unavailable", error_type=type(exc).__name__)
        return None
    return key if isinstance(key, rsa.RSAPublicKey) else None


def verify_signature(raw_body: bytes, signature: Optional[str], timestamp: Optional[str],
                     algorithm: Optional[str], *, public_key_pem: Optional[bytes] = None,
                     now: Optional[float] = None) -> bool:
    """RSA SHA-256 over ``{timestamp}.{raw_body}``; anything unverifiable is refused."""
    if not signature or not timestamp or (algorithm and algorithm.lower() != "rsa-sha256"):
        return False
    try:
        age = abs((time.time() if now is None else now) - int(timestamp))
        decoded = base64.b64decode(signature, validate=True)
    except (ValueError, binascii.Error):
        return False
    key = _public_key(public_key_pem)
    if age > REPLAY_WINDOW_S or key is None:
        return False
    try:
        key.verify(decoded, timestamp.encode("utf-8") + b"." + raw_body, padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        return False
    return True


def _level(regions: Mapping[str, str], place: str) -> str:
    """A place's level: an alert above it covers it whole, one below it covers a part."""
    line = _lineage(place)
    active = {region: level for region, level in regions.items() if region in line or place in _lineage(region)}
    if not active:
        return "N"
    if "R" in active.values():
        return "R"
    return "Y" if any(region in line for region in active) else "P"


def read_snapshot(path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """What the webhook last left on disk, or ``None`` before the first event."""
    try:
        return json.loads((path or state_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def snapshot_text(snapshot: Mapping[str, Any]) -> str:
    regions = snapshot.get("regions") or {}
    levels = {state: _level(regions, state) for state in {PARENTS.get(r) for r in regions} if state in STATES}
    lines = [f"• {STATES[state]}: {_LEVEL_NAMES[level]}" for state, level in sorted(levels.items(), key=lambda x: STATES[x[0]])]
    head = "Повітряна тривога:" if lines else "За подіями вебхука активних тривог немає."
    return "\n".join([head, *lines, f"Остання подія: {snapshot.get('last_event_at')}. Джерело: ukrainealarm.com"])


def _choice_path(path: Optional[Path]) -> Path:
    return (path or state_path()).with_name("regions.json")


def chosen_places(path: Optional[Path] = None) -> Optional[List[str]]:
    """Regions the operator wants to hear about; ``None`` means all of Ukraine."""
    try:
        saved = json.loads(_choice_path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    chosen = [place for place in saved if place in NAMES] if isinstance(saved, list) else []
    return chosen or None


def _label(place: str) -> str:
    return ", ".join(NAMES[region] for region in _lineage(place))


def _entries(places: List[str]) -> List[str]:
    return [f"{place} — {_label(place)}" for place in sorted(places, key=_label)]


def _plain(text: str) -> str:
    """Case and the two apostrophes (the source mixes them) never decide a match."""
    return text.strip().lower().replace("’", "'").replace("ʼ", "'")


def _find(part: str) -> List[str]:
    """An id, an exact name, then oblasts, then anything containing the text."""
    if part.isdigit():
        return [part] if part in NAMES else []
    wanted = _plain(part)
    exact = [region for region, name in NAMES.items() if _plain(name) == wanted]
    if exact:
        return exact
    found = [region for region, name in NAMES.items() if wanted in _plain(name)]
    return [region for region in found if region in STATES] or found


def _unclear(part: str, found: List[str]) -> str:
    """Why a part cannot be used as it stands; empty when it can."""
    if not found:
        return f"Не знайшов «{part}», вибір не змінено. Список: /regions"
    if len(found) > 1 and not all(region in STATES for region in found):
        lines = _entries(found)
        more = [f"…і ще {len(lines) - MAX_CANDIDATES}, уточни назву."] if len(lines) > MAX_CANDIDATES else []
        return "\n".join([f"«{part}» підходить кільком місцям, вибери за номером:", *lines[:MAX_CANDIDATES], *more])
    return ""


def _parse_places(text: str) -> Tuple[List[str], str]:
    """Regions named in the text, or the reason nothing may change."""
    parts = re.split(r"[,\s]+", text) if re.fullmatch(r"[\d,\s]+", text) else text.split(",")
    places: List[str] = []
    for part in filter(None, map(str.strip, parts)):
        found = _find(part)
        problem = _unclear(part, found)
        if problem:
            return [], problem
        places.extend(place for place in found if place not in places)
    return places, "" if places else "Напиши, що вибрати. Список: /regions"


def _choice_text(chosen: Optional[List[str]]) -> str:
    names = "вся Україна" if chosen is None else "; ".join(sorted(_label(place) for place in chosen))
    return f"Сповіщення про тривоги: {names}."


def _regions_help(chosen: Optional[List[str]]) -> str:
    return "\n".join([_choice_text(chosen),
                      "/regions Вінницька, 206 — замінити вибір (назва або номер)",
                      "/regions + Тульчинський район — додати",
                      "/regions - 206 — прибрати",
                      "/regions список Вінницька — райони області",
                      "/regions список Тульчинський район — громади району",
                      "/regions всі — уся Україна", "", *_entries(list(STATES))])


def _children_reply(text: str) -> Dict[str, Any]:
    if not text:
        return {"status": "error", "response": "Напиши: /regions список Вінницька"}
    found = _find(text)
    problem = _unclear(text, found)
    if problem or len(found) > 1:  # several oblasts can be chosen together, but one list is shown
        return {"status": "error", "response": problem or "\n".join([f"«{text}» — кілька областей:", *_entries(found)])}
    children = [region for region, parent in UP.items() if parent == found[0]]
    if not children:
        return {"status": "completed", "response": f"У «{NAMES[found[0]]}» немає дрібніших регіонів."}
    lines = [f"{child} — {NAMES[child]}" for child in sorted(children, key=NAMES.__getitem__)]
    return {"status": "completed", "response": "\n".join([f"{_label(found[0])}:", *lines])}


def _changed(arg: str, current: Optional[List[str]]) -> Tuple[List[str], str]:
    """The new choice for a /regions argument, or the reason it stays as it was."""
    if arg.lower() in {"всі", "все", "вся", "all"}:
        return [], ""
    sign = arg[0] if arg[0] in "+-" else ""
    places, problem = _parse_places(arg[1:] if sign else arg)
    if problem or not sign:
        return places, problem
    if sign == "+":
        return [*(current or []), *(place for place in places if place not in (current or []))], ""
    if current is None:
        return [], "Зараз вибрана вся Україна, прибирати нема з чого. Вибери місця: /regions"
    return [place for place in current if place not in places], ""


def regions_reply(arg: str, path: Optional[Path] = None) -> Dict[str, Any]:
    """/regions: show or change the notified places. The whole country stays tracked."""
    arg = arg.strip()
    if not arg:
        return {"status": "completed", "response": _regions_help(chosen_places(path))}
    head, _, rest = arg.partition(" ")
    if head.lower() == "список":
        return _children_reply(rest.strip())
    chosen, problem = _changed(arg, chosen_places(path))
    if problem:
        return {"status": "error", "response": problem}
    try:
        _choice_path(path).write_text(json.dumps(chosen), encoding="utf-8")
    except OSError as exc:
        logger.warning("alert_choice_not_saved", error_type=type(exc).__name__)
        return {"status": "unavailable", "reason": "not_saved", "response": "Не вдалося зберегти вибір, він не змінився."}
    return {"status": "completed", "response": _choice_text(chosen or None)}


class AlertWatch:
    def __init__(self, gateway: Any, *, path: Optional[Path] = None) -> None:
        self._gateway = gateway
        self._path = path
        self._seen: Deque[str] = deque(maxlen=4096)
        self._pending: List[str] = []
        saved = read_snapshot(path) or {}
        self._regions: Dict[str, str] = dict(saved.get("regions") or {})
        self._trackers: Dict[str, AlertTracker] = {}  # only what is notified, so silence spends no phrases

    def accept(self, raw_body: bytes, signature: Optional[str], timestamp: Optional[str],
               algorithm: Optional[str], *, public_key_pem: Optional[bytes] = None) -> bool:
        if not verify_signature(raw_body, signature, timestamp, algorithm, public_key_pem=public_key_pem):
            logger.warning("ukrainealarm_webhook_refused")
            return False
        digest = hashlib.sha256(f"{timestamp}.".encode("utf-8") + raw_body).hexdigest()
        if digest in self._seen:
            return False
        self._seen.append(digest)
        return True

    def handle(self, event: Any) -> None:
        """Replace one region's snapshot and queue a phrase for each notified place that changed level."""
        if not isinstance(event, Mapping) or event.get("alarmType") != "AIR":
            return  # the phrases describe air raids; other alarm types are not guessed into them
        region, levels = str(event.get("regionId")), event.get("activeAlertLevels")
        if region not in NAMES or not isinstance(levels, list):
            logger.warning("ukrainealarm_event_ignored", region=region)
            return
        places = chosen_places(self._path) or list(STATES)
        self._trackers = {place: self._trackers.get(place) or self._baseline(place) for place in places}
        if levels:
            red = any(isinstance(x, Mapping) and str(x.get("alertLevel")).lower() == "red" for x in levels)
            self._regions[region] = "R" if red else "Y"
        else:
            self._regions.pop(region, None)
        for place, tracker in self._trackers.items():
            note = tracker.update(_level(self._regions, place))
            if note:
                mark, _, phrase = note.partition(" ")
                self._pending.append(f"{mark} {_label(place)}: {phrase}")
        self._save()

    def _baseline(self, place: str) -> AlertTracker:
        """A newly watched place starts from the stored levels, so its all-clear is real."""
        tracker = AlertTracker()
        tracker.update(_level(self._regions, place))  # says nothing
        return tracker

    def _save(self) -> None:
        snapshot = {"regions": self._regions, "last_event_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        path = self._path or state_path()
        spare = path.with_suffix(".tmp")
        try:
            spare.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
            spare.replace(path)
        except OSError as exc:
            logger.warning("alert_state_not_saved", error_type=type(exc).__name__)

    async def flush(self) -> None:
        """Send what is queued; a message Telegram refused stays for the next round."""
        batch = self._pending[:BATCH]
        owner = await self._gateway.owner_user_id() if batch else None
        if owner and await self._gateway.send(ALERT_BOT, owner, "\n\n".join(batch)):
            del self._pending[: len(batch)]

    async def loop(self) -> None:
        while True:
            try:
                await self.flush()
            except Exception as exc:  # noqa: BLE001 - one bad round must not end the watch
                logger.warning("alert_watch_flush_failed", error_type=type(exc).__name__)
            await asyncio.sleep(FLUSH_INTERVAL_S)
