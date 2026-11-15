"""A picture of the alert levels in one oblast, or of all Ukraine, for Alice's cards (15.11.2026).

Borders come from ``alert_map_shapes.json``, built by ``tools/build_alert_map.py`` from OCHA COD-AB
Ukraine v05 (SSPE «Kartographia», CC BY-IGO). The levels are the ones the watch already holds;
nothing is fetched here. A region without a border (occupied areas, a few renamed communities)
takes its district's colour, which is drawn underneath; an oblast without borders gets no map
rather than a guessed one.
"""
from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

import structlog

logger = structlog.get_logger(__name__)

SHAPES_PATH = Path(__file__).with_name("alert_map_shapes.json")
TREE_PATH = Path(__file__).with_name("ukrainealarm_regions.json")
WIDTH = 900
PAD = 24
SCALE = 2  # drawn twice as large, then reduced: smooth edges without extra libraries
KYIV = ZoneInfo("Europe/Kyiv")
#: Fill per level: red alert, yellow danger, part of the area, quiet.
FILL = {"R": (214, 40, 40), "Y": (244, 196, 48), "P": (250, 226, 140), "N": (226, 232, 226)}
LINE = {"community": (150, 150, 150), "district": (70, 70, 70), "oblast": (20, 20, 20), "chosen": (25, 90, 220)}
WIDTHS = {"community": 1, "district": 2, "oblast": 3, "chosen": 4}
ATTRIBUTION = "Межі: OCHA / ДНВП «Картографія», CC BY-IGO"

Ring = List[List[float]]


@lru_cache(maxsize=1)
def _data() -> Dict[str, Dict]:
    try:
        data = json.loads(SHAPES_PATH.read_text(encoding="utf-8"))
        return {"shapes": data["shapes"], "attached": data.get("attached", {})}
    except (OSError, ValueError, KeyError) as exc:
        logger.warning("alert_map_shapes_unreadable", error_type=type(exc).__name__)
        return {"shapes": {}, "attached": {}}


def shapes() -> Dict[str, List[Ring]]:
    return _data()["shapes"]


def oblast_of(place: str) -> Optional[str]:
    """The oblast whose map shows this place: the top of its lineage, or, for a city community at
    the top of the alarm tree (Харків, Запоріжжя), the oblast it lies in."""
    attached = _data()["attached"]
    if place in attached:
        return attached[place]
    tree = _tree()
    while place in tree and tree[place][1] is not None:
        place = str(tree[place][1])
    return place if place in tree else None


@lru_cache(maxsize=1)
def _tree() -> Dict[str, Tuple[str, Optional[str]]]:
    regions = json.loads(TREE_PATH.read_text(encoding="utf-8"))["regions"]
    return {ident: (entry[0], entry[1]) for ident, entry in regions.items()}


def children(parent: Optional[str]) -> List[str]:
    return sorted(ident for ident, (_name, up) in _tree().items() if up == parent)


def _box(rings: Iterable[Ring]) -> Optional[Tuple[float, float, float, float]]:
    points = [point for ring in rings for point in ring]
    if not points:
        return None
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


class _Canvas:
    """Longitude/latitude to pixels, with longitude shrunk by the cosine of the middle latitude."""

    def __init__(self, box: Tuple[float, float, float, float]) -> None:
        from math import cos, radians

        west, south, east, north = box
        self.west, self.north = west, north
        self.stretch = cos(radians((south + north) / 2))
        span_x, span_y = max((east - west) * self.stretch, 1e-6), max(north - south, 1e-6)
        self.unit = (WIDTH - 2 * PAD) * SCALE / span_x
        self.width = WIDTH * SCALE
        self.height = int(span_y * self.unit + 2 * PAD * SCALE)

    def points(self, ring: Ring) -> List[Tuple[float, float]]:
        pad = PAD * SCALE
        return [(pad + (x - self.west) * self.stretch * self.unit, pad + (self.north - y) * self.unit)
                for x, y in ring]


def _layers(oblast: Optional[str]) -> Tuple[List[str], List[str], List[str]]:
    """(oblasts, districts, communities) to draw: one oblast in detail, or the oblasts of Ukraine."""
    if oblast is None:
        return [o for o in children(None) if o not in _data()["attached"]], [], []
    districts = children(oblast)
    cities = [city for city, home in _data()["attached"].items() if home == oblast]
    return [oblast], districts, [c for d in districts for c in children(d)] + sorted(cities)


def render(level_of: Callable[[str], str], oblast: Optional[str], chosen: Sequence[str] = ()) -> Optional[bytes]:
    """PNG of the levels, or None when the borders are missing (never a guessed shape)."""
    from PIL import Image, ImageDraw

    known = shapes()
    oblasts, districts, communities = _layers(oblast)
    box = _box(ring for ident in oblasts for ring in known.get(ident, []))
    if box is None:
        return None
    canvas = _Canvas(box)
    image = Image.new("RGB", (canvas.width, canvas.height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    fills = districts + communities if oblast else oblasts
    for ident in fills:  # districts first: a community without a border keeps its district's colour
        for ring in known.get(ident, []):
            draw.polygon(canvas.points(ring), fill=FILL.get(level_of(ident), FILL["N"]))
    outlines = [("community", communities), ("district", districts), ("oblast", oblasts),
                ("chosen", [c for c in chosen if c in known])]
    for kind, idents in outlines:
        for ident in idents:
            for ring in known.get(ident, []):
                draw.line(canvas.points(ring), fill=LINE[kind], width=WIDTHS[kind] * SCALE, joint="curve")
    image = image.resize((canvas.width // SCALE, canvas.height // SCALE), Image.LANCZOS)
    out = io.BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


def caption(oblast: Optional[str], now: Optional[datetime] = None) -> str:
    where = _tree()[oblast][0] if oblast else "Україна"
    moment = (now or datetime.now(timezone.utc)).astimezone(KYIV).strftime("%H:%M")
    return (f"🗺️ {where} · стан на {moment}\n"
            f"🔴 тривога  🟡 небезпека  блідо-жовте — частина  🟦 рамка — твоє місце\n{ATTRIBUTION}")
