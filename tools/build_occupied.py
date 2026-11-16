"""Build ``src/alert_occupied.json``: the currently occupied areas for the alert map (15.11.2026).

Source: the official «Перелік територій, на яких ведуться (велися) бойові дії або тимчасово
окупованих Російською Федерацією», order No. 376 of the Ministry for Development (now the Ministry
for Restoration), as published on zakon.rada.gov.ua (z0380-25) in three .docx annexes. Andrii chose
this list over DeepState on 15.11.2026. zakon.rada.gov.ua does not answer from the server's
foreign address, so the annexes are fetched elsewhere and the folder is passed here.

A settlement is occupied now when its row says «Тимчасово окупована …» and has no end date (an
end date means it was liberated). Settlement codes (КАТОТТГ, 19 characters) begin with the OCHA
settlement pcode (12 characters), so no names are matched. A community whose every OCHA settlement
is occupied is painted whole; in a partly occupied community only the occupied settlements are.

Usage: python -m tools.build_occupied <folder with the .docx annexes> <folder with ukr_admin3/4.geojson>
"""
from __future__ import annotations

import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple
from xml.etree import ElementTree

from tools.build_alert_map import rings

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "alert_occupied.json"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
OCCUPIED = "окупована"
TOLERANCE = 0.004  # degrees, like the communities of the map
SETTLEMENT_TOLERANCE = 0.002


def table_rows(path: Path) -> Iterable[List[str]]:
    """Every row of every table of a .docx, as cell texts (standard library only)."""
    root = ElementTree.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    for table in root.iter(W + "tbl"):
        for row in table.findall(W + "tr"):
            yield ["".join(text.text or "" for text in cell.iter(W + "t")).strip() for cell in row.findall(W + "tc")]


def occupied_now(rows: Iterable[List[str]]) -> Set[str]:
    """OCHA settlement pcodes occupied now: an «окупована» row with no end date (column 8)."""
    return {row[4][:12] for row in rows
            if len(row) >= 8 and row[4].startswith("UA") and OCCUPIED in row[5].lower() and not row[7].strip()}


def _features(folder: Path, level: int) -> List[Dict[str, Any]]:
    return json.loads((folder / f"ukr_admin{level}.geojson").read_text(encoding="utf-8"))["features"]


def split(settlements: List[Dict[str, Any]], occupied: Set[str]) -> Tuple[Set[str], Set[str]]:
    """(wholly occupied community pcodes, occupied settlement pcodes in partly occupied communities)."""
    counts: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
    for feature in settlements:
        props = feature["properties"]
        counts[props["adm3_pcode"]][0] += 1
        counts[props["adm3_pcode"]][1] += props["adm4_pcode"] in occupied
    whole = {code for code, (total, taken) in counts.items() if total and taken == total}
    partial = {props["adm4_pcode"] for props in (f["properties"] for f in settlements)
               if props["adm4_pcode"] in occupied and props["adm3_pcode"] not in whole}
    return whole, partial


def build(annexes: Path, bounds: Path) -> Dict[str, Any]:
    rows = [row for path in sorted(annexes.glob("*.docx")) for row in table_rows(path)]
    occupied = occupied_now(rows)
    settlements = _features(bounds, 4)
    whole, partial = split(settlements, occupied)
    areas = [ring for f in _features(bounds, 3) if f["properties"]["adm3_pcode"] in whole
             for ring in rings(f["geometry"], TOLERANCE)]
    areas += [ring for f in settlements if f["properties"]["adm4_pcode"] in partial
              for ring in rings(f["geometry"], SETTLEMENT_TOLERANCE)]
    return {"source": "Перелік ТОТ, наказ Мінрозвитку № 376 (z0380-25), zakon.rada.gov.ua",
            "settlements": len(occupied), "communities": len(whole), "partial_settlements": len(partial),
            "areas": areas}


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    data = build(Path(argv[1]), Path(argv[2]))
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{data['settlements']} occupied settlements, {data['communities']} whole communities, "
          f"{data['partial_settlements']} settlements in partly occupied ones, {len(data['areas'])} rings, "
          f"{OUT.stat().st_size // 1024} KiB")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
