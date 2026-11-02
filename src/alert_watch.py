"""Air-raid watch: signed Ukraine Alarm webhooks -> the operator's phrases -> Alice's Telegram bot.

The API refuses the server's address, so Ukraine Alarm pushes events to
``/webhook/ukrainealarm``. Each event carries a snapshot of the region's active levels,
which replaces the stored state (``status`` alone can describe one of several causes).
Districts and communities roll up into their oblast, so all of Ukraine fits one bot.
No model is called. An event that is unsigned, stale or repeated changes nothing.
"""
from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import json
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Mapping, Optional

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
_TABLE = json.loads(Path(__file__).with_name("ukrainealarm_regions.json").read_text(encoding="utf-8"))
STATES: Dict[str, str] = _TABLE["states"]
PARENTS: Dict[str, str] = _TABLE["parents"]
_LEVEL_NAMES = {"R": "червоний", "Y": "жовтий", "P": "частина області"}


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


def _state_level(regions: Mapping[str, str], state: str) -> str:
    """Oblast level from its own and its children's stored levels."""
    active = {region: level for region, level in regions.items() if PARENTS.get(region) == state}
    if not active:
        return "N"
    if "R" in active.values():
        return "R"
    return "Y" if state in active else "P"


def read_snapshot(path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """What the webhook last left on disk, or ``None`` before the first event."""
    try:
        return json.loads((path or state_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def snapshot_text(snapshot: Mapping[str, Any]) -> str:
    regions = snapshot.get("regions") or {}
    levels = {state: _state_level(regions, state) for state in {PARENTS.get(r) for r in regions} if state in STATES}
    lines = [f"• {STATES[state]}: {_LEVEL_NAMES[level]}" for state, level in sorted(levels.items(), key=lambda x: STATES[x[0]])]
    head = "Повітряна тривога:" if lines else "За подіями вебхука активних тривог немає."
    return "\n".join([head, *lines, f"Остання подія: {snapshot.get('last_event_at')}. Джерело: ukrainealarm.com"])


class AlertWatch:
    def __init__(self, gateway: Any, *, path: Optional[Path] = None) -> None:
        self._gateway = gateway
        self._path = path
        self._seen: Deque[str] = deque(maxlen=4096)
        self._pending: List[str] = []
        saved = read_snapshot(path) or {}
        self._regions: Dict[str, str] = dict(saved.get("regions") or {})
        self._trackers: Dict[str, AlertTracker] = {}
        for state in STATES:
            self._trackers[state] = AlertTracker()
            self._trackers[state].update(_state_level(self._regions, state))  # baseline, says nothing

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
        """Replace one region's snapshot and queue a phrase if its oblast changed level."""
        if not isinstance(event, Mapping) or event.get("alarmType") != "AIR":
            return  # the phrases describe air raids; other alarm types are not guessed into them
        region, levels = str(event.get("regionId")), event.get("activeAlertLevels")
        state = PARENTS.get(region)
        if state is None or not isinstance(levels, list):
            logger.warning("ukrainealarm_event_ignored", region=region)
            return
        if levels:
            red = any(isinstance(x, Mapping) and str(x.get("alertLevel")).lower() == "red" for x in levels)
            self._regions[region] = "R" if red else "Y"
        else:
            self._regions.pop(region, None)
        note = self._trackers[state].update(_state_level(self._regions, state))
        if note:
            mark, _, phrase = note.partition(" ")
            self._pending.append(f"{mark} {STATES[state]}: {phrase}")
        self._save()

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
