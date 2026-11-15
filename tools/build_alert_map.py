"""Build ``src/alert_map_shapes.json``: simplified borders keyed by Ukraine Alarm region id (15.11.2026).

Source: OCHA COD-AB Ukraine v05 (SSPE «Kartographia», valid 2025-09-01, CC BY-IGO),
https://data.humdata.org/dataset/cod-ab-ukr — the ``ukr_admin{1,2,3}.geojson`` files of
``ukr_admin_boundaries.geojson.zip``. The archive is not kept in the repository.

Usage: python -m tools.build_alert_map <folder with ukr_admin1..3.geojson>

Regions are matched by Ukrainian name inside their parent («Березівський район» under its oblast
↔ adm2 «Березівський»). Whatever cannot be matched is listed, never guessed onto another shape.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
TREE = ROOT / "src" / "ukrainealarm_regions.json"
OUT = ROOT / "src" / "alert_map_shapes.json"
PLACES = ROOT / "src" / "alert_places.json"
TOLERANCE = {1: 0.01, 2: 0.006, 3: 0.004}  # degrees; ~1 km, 600 m, 400 m
_SUFFIXES = (" область", " район", " територіальна громада", " міська", " селищна", " сільська")


#: Raions renamed in 2024–2025: OCHA has the new name, the alarm tree still the old one.
RENAMED = {"володимирський": "володимир-волинський", "берестинський": "красноградський"}


def key(name: str) -> str:
    """A comparable name: lower case, no «м.», no level words, one apostrophe.

    A city community in the alarm tree is «м. Вінниця та Вінницька територіальна громада»: the
    community's own name is the part after «та».
    """
    text = name.lower().replace("’", "'").replace("ʼ", "'").replace("`", "'")
    text = re.sub(r"^м\.\s*[^,]*?\s+та\s+", "", text)
    text = re.sub(r"^м\.\s*", "", text)
    for suffix in _SUFFIXES:
        text = text.replace(suffix, "")
    text = re.sub(r"\s+", " ", text).strip()
    return RENAMED.get(text, text)


def _perp(p: List[float], a: List[float], b: List[float]) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == dy == 0:
        return abs(p[0] - a[0]) + abs(p[1] - a[1])
    return abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / (dx * dx + dy * dy) ** 0.5


def simplify(points: List[List[float]], tolerance: float) -> List[List[float]]:
    """Douglas–Peucker without recursion; keeps the first and last point."""
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        best, index = 0.0, 0
        for i in range(first + 1, last):
            distance = _perp(points[i], points[first], points[last])
            if distance > best:
                best, index = distance, i
        if best > tolerance:
            keep[index] = True
            stack += [(first, index), (index, last)]
    return [[round(x, 3), round(y, 3)] for (x, y), kept in zip(points, keep, strict=True) if kept]


def rings(geometry: Dict[str, Any], tolerance: float) -> List[List[List[float]]]:
    """Outer rings only (holes are not drawn), simplified; rings that collapse are dropped."""
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    out = [simplify(polygon[0], tolerance) for polygon in polygons]
    return [ring for ring in out if len(ring) >= 4]


def _features(folder: Path, level: int) -> Iterable[Dict[str, Any]]:
    return json.loads((folder / f"ukr_admin{level}.geojson").read_text(encoding="utf-8"))["features"]


def _children(tree: Dict[str, List[Optional[str]]]) -> Dict[Optional[str], Dict[str, str]]:
    out: Dict[Optional[str], Dict[str, str]] = {}
    for ident, (name, parent) in tree.items():
        group = TOP_COMMUNITY if parent is None and "громада" in name else parent
        out.setdefault(group, {})[key(name)] = ident
    return out


TOP_COMMUNITY = "top-community"  # Харків, Запоріжжя: communities at the top of the alarm tree


def _top_community(by_parent: Dict[Optional[str], Dict[str, str]], name: str, oblast: str) -> Optional[str]:
    """A top-level city community, only when its name and its oblast's name agree."""
    ident = by_parent.get(TOP_COMMUNITY, {}).get(name)
    return ident if ident and key(oblast) == name else None


def _lookup(props: Dict[str, Any], level: int, parent: Optional[str],
            by_parent: Dict[Optional[str], Dict[str, str]]) -> Optional[str]:
    if level > 1 and parent is None:
        return None  # its district did not match: never look among the oblasts («Луганська» громада)
    names = [key(props[f"adm{level}_name1"])]
    if props.get(f"adm{level}_name1_old"):
        names.append(key(props[f"adm{level}_name1_old"]))
    for name in names:
        ident = by_parent.get(parent, {}).get(name)
        if ident:
            return ident
    return _top_community(by_parent, names[0], props["adm1_name1"]) if level == 3 else None


def _match(folder: Path, level: int, by_parent: Dict[Optional[str], Dict[str, str]],
           parent_of: Dict[str, str], attached: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, str], List[str]]:
    """Shapes of one level, the pcode → alarm id map for the next level, and what did not match.

    A city community found at the top of the alarm tree is recorded in ``attached`` under the
    oblast its OCHA district belongs to, so the oblast's map can draw it.
    """
    shapes, ids, missing = {}, {}, []
    for feature in _features(folder, level):
        props = feature["properties"]
        parent = parent_of.get(props.get(f"adm{level - 1}_pcode", ""), None) if level > 1 else None
        ident = _lookup(props, level, parent, by_parent)
        if ident is None or ident in shapes:
            missing.append(f"adm{level} {props[f'adm{level}_pcode']} {props[f'adm{level}_name1']}")
            continue
        if level == 3 and ident in by_parent.get(TOP_COMMUNITY, {}).values() and parent:
            attached[ident] = _oblast_of_district(by_parent, parent)
        ids[props[f"adm{level}_pcode"]] = ident
        shapes[ident] = rings(feature["geometry"], TOLERANCE[level])
    return shapes, ids, missing


def _oblast_of_district(by_parent: Dict[Optional[str], Dict[str, str]], district: str) -> str:
    return next(parent for parent, names in by_parent.items() if district in names.values())


def build(folder: Path) -> Tuple[Dict[str, Any], Dict[str, str], List[str], Dict[str, str]]:
    """Shapes by alarm id, top cities attached to oblasts, what did not match, oblast pcode → alarm id."""
    tree = json.loads(TREE.read_text(encoding="utf-8"))["regions"]
    by_parent = _children(tree)
    shapes: Dict[str, Any] = {}
    attached: Dict[str, str] = {}
    missing: List[str] = []
    parents: Dict[str, str] = {}
    oblasts: Dict[str, str] = {}
    for level in (1, 2, 3):
        found, parents, lost = _match(folder, level, by_parent, parents, attached)
        oblasts = oblasts or dict(parents)
        missing += lost + [f"adm{level} {ident} already has a border" for ident in found if ident in shapes]
        shapes.update({ident: rings_ for ident, rings_ in found.items() if ident not in shapes})
    return shapes, attached, missing, oblasts


def places(folder: Path, oblasts: Dict[str, str]) -> Dict[str, Dict[str, List[float]]]:
    """Settlement points by oblast alarm id, for placing an Air Force message on the map.

    A name that two settlements of one oblast share is kept only when exactly one of them is a city;
    otherwise it is left out, so a marker never lands on the wrong village.
    """
    kinds = {f["properties"]["adm4_pcode"]: f["properties"].get("adm4_type1") for f in _features(folder, 4)}
    found: Dict[str, Dict[str, List[Tuple[bool, List[float]]]]] = {}
    for feature in json.loads((folder / "ukr_adminpoints.geojson").read_text(encoding="utf-8"))["features"]:
        props = feature["properties"]
        oblast = oblasts.get(props.get("adm1_pcode") or "")
        if props.get("admin_level") != 4 or not oblast or not props.get("name1"):
            continue
        city = kinds.get(props.get("adm4_pcode")) == "Місто"
        point = [round(props["x_coord"], 3), round(props["y_coord"], 3)]
        found.setdefault(oblast, {}).setdefault(props["name1"].replace("’", "'"), []).append((city, point))
    out: Dict[str, Dict[str, List[float]]] = {}
    for oblast, names in found.items():
        for name, options in names.items():
            cities = [point for city, point in options if city]
            point = options[0][1] if len(options) == 1 else (cities[0] if len(cities) == 1 else None)
            if point:
                out.setdefault(oblast, {})[name] = point
    return out


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    shapes, attached, missing, oblasts = build(Path(argv[1]))
    source = "OCHA COD-AB Ukraine v05 (SSPE Kartographia, 2025-09-01), CC BY-IGO"
    data = {"source": source, "attached": attached, "shapes": shapes}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    points = places(Path(argv[1]), oblasts)
    PLACES.write_text(json.dumps({"source": source, "places": points}, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    print(f"{len(shapes)} shapes, {OUT.stat().st_size // 1024} KiB, {len(missing)} unmatched; "
          f"{sum(len(p) for p in points.values())} places, {PLACES.stat().st_size // 1024} KiB")
    for line in missing:
        print("  unmatched:", line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
