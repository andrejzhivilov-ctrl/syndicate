"""A picture of the alert levels in one oblast and around it, or of all Ukraine (15.11.2026).

Borders come from ``alert_map_shapes.json``, built by ``tools/build_alert_map.py`` from OCHA COD-AB
Ukraine v05 (SSPE «Kartographia», CC BY-IGO). The levels are the ones the watch already holds;
nothing is fetched here. Dark style at the operator's request: quiet areas slate, danger mustard,
alert salmon red, every community coloured by its own level, so a quiet city with an alert next
door shows both. A region without a border (occupied areas, a few renamed communities) takes its
district's colour, which is drawn underneath; an oblast without borders gets no map at all.

Threat markers (``Marker``) come from the Air Force's messages (``src/threat_watch.py``): a white
sign at the named settlement and, when the message gives one, an arrow from where it comes.
They show what the message says, never a measured track.
"""
from __future__ import annotations

import io
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from math import cos, hypot, radians
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from zoneinfo import ZoneInfo

import structlog

logger = structlog.get_logger(__name__)

SHAPES_PATH = Path(__file__).with_name("alert_map_shapes.json")
TREE_PATH = Path(__file__).with_name("ukrainealarm_regions.json")
WIDTH = 900
PAD = 24
SCALE = 2  # drawn twice as large, then reduced: smooth edges without extra libraries
AROUND = 0.15  # an oblast map also shows this share of its size around it
KYIV = ZoneInfo("Europe/Kyiv")
BACKGROUND = (30, 33, 43)
QUIET = (58, 62, 79)
FILL = {"R": (224, 103, 95), "Y": (201, 162, 39)}  # anything else (quiet, «part of») is QUIET
LINE = {"community": (70, 74, 92), "district": (88, 93, 114), "oblast": (24, 26, 34),
        "focus": (210, 214, 226), "chosen": (110, 170, 255)}
WIDTHS = {"community": 1, "district": 1, "oblast": 2, "focus": 3, "chosen": 3}
TEXT = (236, 238, 244)
FONT_PATHS = ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf")
MONTHS = ("січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня",
          "жовтня", "листопада", "грудня")
ATTRIBUTION = "Межі: OCHA / ДНВП «Картографія», CC BY-IGO"

Ring = List[List[float]]
Box = Tuple[float, float, float, float]


@dataclass(frozen=True)
class Marker:
    kind: str  # "drone", "missile", "kab", "other"
    lon: float
    lat: float
    origin: Optional[Tuple[float, float]] = None  # where it comes from, when the message says


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


@lru_cache(maxsize=1)
def _tree() -> Dict[str, Tuple[str, Optional[str]]]:
    regions = json.loads(TREE_PATH.read_text(encoding="utf-8"))["regions"]
    return {ident: (entry[0], entry[1]) for ident, entry in regions.items()}


def children(parent: Optional[str]) -> List[str]:
    return sorted(ident for ident, (_name, up) in _tree().items() if up == parent)


def oblasts() -> List[str]:
    """The oblasts (and м. Київ) — the top of the tree without the attached city communities."""
    return [ident for ident in children(None) if ident not in _data()["attached"]]


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
def _depths() -> Dict[str, int]:
    """0 oblast, 1 district, 2 community; attached city communities count as communities."""
    out = {}
    for ident in shapes():
        depth, up = 0, _tree().get(ident, ("", None))[1]
        while up is not None:
            depth, up = depth + 1, _tree()[up][1]
        out[ident] = 2 if ident in _data()["attached"] else depth
    return out


def _box(rings: Iterable[Ring]) -> Optional[Box]:
    points = [point for ring in rings for point in ring]
    if not points:
        return None
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


@lru_cache(maxsize=None)
def _box_of(ident: str) -> Optional[Box]:
    return _box(shapes().get(ident, []))


def _overlaps(a: Box, b: Box) -> bool:
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def _centre(ring: Ring) -> Tuple[float, float]:
    """The area centroid of a ring (falls back to the mean point for a degenerate one)."""
    area = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:], strict=False):
        step = x0 * y1 - x1 * y0
        area += step
        cx += (x0 + x1) * step
        cy += (y0 + y1) * step
    if abs(area) < 1e-12:
        return sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
    return cx / (3 * area), cy / (3 * area)


def label_point(ident: str) -> Optional[Tuple[float, float]]:
    rings = shapes().get(ident, [])
    return _centre(max(rings, key=len)) if rings else None


class _Canvas:
    """Longitude/latitude to pixels, with longitude shrunk by the cosine of the middle latitude."""

    def __init__(self, box: Box) -> None:
        west, south, east, north = box
        self.box = box
        self.west, self.north = west, north
        self.stretch = cos(radians((south + north) / 2))
        span_x, span_y = max((east - west) * self.stretch, 1e-6), max(north - south, 1e-6)
        self.unit = (WIDTH - 2 * PAD) * SCALE / span_x
        self.width = WIDTH * SCALE
        self.height = int(span_y * self.unit + 2 * PAD * SCALE)

    def xy(self, lon: float, lat: float) -> Tuple[float, float]:
        pad = PAD * SCALE
        return pad + (lon - self.west) * self.stretch * self.unit, pad + (self.north - lat) * self.unit

    def points(self, ring: Ring) -> List[Tuple[float, float]]:
        return [self.xy(x, y) for x, y in ring]


def _font(size: int) -> Any:
    from PIL import ImageFont

    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size * SCALE)
        except OSError:
            continue
    return None  # no Cyrillic font: the map goes without labels rather than with broken ones


def _view(oblast: Optional[str]) -> Optional[Box]:
    if oblast is None:
        return _box(ring for ident in oblasts() for ring in shapes().get(ident, []))
    box = _box_of(oblast)
    if box is None:
        return None
    dx, dy = (box[2] - box[0]) * AROUND, (box[3] - box[1]) * AROUND
    return box[0] - dx, box[1] - dy, box[2] + dx, box[3] + dy


def _fill(draw: Any, canvas: _Canvas, level_of: Callable[[str], str]) -> None:
    """Every shape in view, oblasts first and communities last, each in its own level's colour."""
    depths = _depths()
    visible = [ident for ident in shapes() if _overlaps(_box_of(ident) or (0, 0, -1, -1), canvas.box)]
    def order(ident: str) -> Tuple[int, float]:  # м. Київ lies inside Київська: smaller ones on top
        box = _box_of(ident) or (0, 0, 0, 0)
        return depths[ident], -(box[2] - box[0]) * (box[3] - box[1])

    for ident in sorted(visible, key=order):
        colour = FILL.get(level_of(ident), QUIET)
        for ring in shapes()[ident]:
            draw.polygon(canvas.points(ring), fill=colour)


def _outline(draw: Any, canvas: _Canvas, kind: str, idents: Iterable[str]) -> None:
    for ident in idents:
        for ring in shapes().get(ident, []):
            draw.line(canvas.points(ring), fill=LINE[kind], width=WIDTHS[kind] * SCALE, joint="curve")


def _short(name: str) -> str:
    for suffix in (" область", " район", " територіальна громада"):
        name = name.replace(suffix, "")
    return name.replace("Автономна Республіка Крим", "А. Р. Крим")


def _labels(draw: Any, canvas: _Canvas, idents: Iterable[str], size: int) -> None:
    font = _font(size)
    if font is None:
        return
    for ident in idents:
        point = label_point(ident)
        if point is None:
            continue
        x, y = canvas.xy(*point)
        if 0 < x < canvas.width and 0 < y < canvas.height:
            draw.text((x, y), _short(_tree()[ident][0]), font=font, fill=TEXT, anchor="mm",
                      stroke_width=SCALE, stroke_fill=BACKGROUND)


def _glyph(draw: Any, at: Tuple[float, float], heading: Tuple[float, float], kind: str) -> None:
    """A white sign: a dart for a drone, a long dart for a missile, a ringed dot for a guided bomb."""
    x, y = at
    hx, hy = heading
    px, py = -hy, hx
    size = 15 * SCALE
    if kind == "kab":
        draw.ellipse((x - size, y - size, x + size, y + size), fill=TEXT, outline=BACKGROUND, width=SCALE)
        draw.ellipse((x - size / 3, y - size / 3, x + size / 3, y + size / 3), fill=BACKGROUND)
        return
    length = size * (2.2 if kind == "missile" else 1.4)
    tip = (x + hx * size, y + hy * size)
    tail = (x - hx * length, y - hy * length)
    wing = size * (0.5 if kind == "missile" else 0.9)
    draw.polygon([tip, (tail[0] + px * wing, tail[1] + py * wing), (x - hx * size * 0.3, y - hy * size * 0.3),
                  (tail[0] - px * wing, tail[1] - py * wing)], fill=TEXT, outline=BACKGROUND, width=SCALE * 2)


def _markers(draw: Any, canvas: _Canvas, markers: Sequence[Marker]) -> None:
    for marker in markers:
        target = canvas.xy(marker.lon, marker.lat)
        heading = (0.0, 1.0)  # pointing down, when no direction is known
        if marker.origin:
            start = canvas.xy(*marker.origin)
            dx, dy = target[0] - start[0], target[1] - start[1]
            norm = hypot(dx, dy) or 1.0
            heading = (dx / norm, dy / norm)
            draw.line([start, target], fill=BACKGROUND, width=5 * SCALE)
            draw.line([start, target], fill=TEXT, width=2 * SCALE)
        _glyph(draw, target, heading, marker.kind)


def _footer(draw: Any, canvas: _Canvas, now: datetime) -> None:
    font = _font(13)
    if font is None:
        return
    local = now.astimezone(KYIV)
    text = f"Станом на {local.day} {MONTHS[local.month - 1]} о {local:%H:%M}"
    draw.text((PAD * SCALE, canvas.height - PAD * SCALE // 2), text, font=font, fill=TEXT, anchor="ls")


def render(level_of: Callable[[str], str], oblast: Optional[str], chosen: Sequence[str] = (),
           markers: Sequence[Marker] = (), now: Optional[datetime] = None) -> Optional[bytes]:
    """PNG of the levels, or None when the borders are missing (never a guessed shape)."""
    from PIL import Image, ImageDraw

    box = _view(oblast)
    if box is None:
        return None
    canvas = _Canvas(box)
    image = Image.new("RGB", (canvas.width, canvas.height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    _fill(draw, canvas, level_of)
    if oblast:
        _outline(draw, canvas, "community", [c for d in children(oblast) for c in children(d)])
        _outline(draw, canvas, "district", children(oblast))
    _outline(draw, canvas, "oblast", oblasts())
    if oblast:
        _outline(draw, canvas, "focus", [oblast])
    _outline(draw, canvas, "chosen", [c for c in chosen if c != oblast])
    if oblast:
        _labels(draw, canvas, children(oblast), 11)
        _labels(draw, canvas, [o for o in oblasts() if o != oblast], 13)
    else:
        _labels(draw, canvas, oblasts(), 11)
    _markers(draw, canvas, markers)  # on top of the labels: a threat is never hidden under a name
    _footer(draw, canvas, now or datetime.now(timezone.utc))
    image = image.resize((canvas.width // SCALE, canvas.height // SCALE), Image.LANCZOS)
    out = io.BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


def caption(oblast: Optional[str], now: Optional[datetime] = None) -> str:
    where = _tree()[oblast][0] if oblast else "Україна"
    moment = (now or datetime.now(timezone.utc)).astimezone(KYIV).strftime("%H:%M")
    return (f"🗺️ {where} · стан на {moment}\n"
            f"🔴 тривога  🟡 небезпека  сіре — спокійно  синя рамка — твоє місце\n{ATTRIBUTION}")
