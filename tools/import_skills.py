"""Vendor SKILL.md files from pinned repositories into the skill hub as reference only.

    python tools/import_skills.py <checkouts_dir> <report.json> owner/repo@commit:skills_root ... [--with-references=id,...]

``<checkouts_dir>/<owner>_<repo>`` must be a clone at that exact commit. Nothing from it is
executed: only SKILL.md and LICENSE are copied. Each SKILL.md is screened for prompt
injection, hidden characters, remote execution and detection evasion; a flagged skill is
left out and listed in the report. New entries are assigned to no agent: an agent gets a
skill only through its profile, and the screen is not a human review.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config" / "skill_library.json"
MAX_BYTES = 256_000
REVIEW = ("Automated screen {date}: prompt injection, hidden characters, remote execution, "
          "detection evasion. Not a human review and not a permission grant.")
FLAGS = {
    "prompt_injection": re.compile(
        r"ignore (all |any )?(previous|prior|above) (instructions|prompts|rules)"
        r"|disregard (all |any )?(previous|prior|the system)"
        r"|you are now (in )?(developer|dan|jailbreak)", re.IGNORECASE),
    "remote_execution": re.compile(
        r"(curl|wget)[^\n|]{0,200}\|\s*(sudo\s+)?(ba|z)?sh\b|invoke-expression|\biex\s*\("
        r"|base64\s+(-d|--decode)[^\n]{0,80}\|\s*(ba)?sh", re.IGNORECASE),
    "detection_evasion": re.compile(
        r"anti-?detect|undetect|fingerprint (spoof|evasion|randomi)|stealth (mode|browser|plugin)"
        r"|captcha (solv|bypass)|bypass (bot|captcha|cloudflare|rate.?limit)|residential prox", re.IGNORECASE),
    "credential_exfiltration": re.compile(
        r"(send|post|upload|exfiltrat)\w*[^\n]{0,60}(api[_ -]?key|token|password|credential|\.env)"
        r"[^\n]{0,60}(https?://)", re.IGNORECASE),
}
HIDDEN = re.compile("[​-‏‪-‮⁦-⁩﻿\U000e0000-\U000e007f]")
_FIELD = re.compile(r"^(name|description):\s*(.*)$")


def front_matter(text: str) -> Dict[str, str]:
    """name and description from the leading YAML block, quotes stripped."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    found: Dict[str, str] = {}
    block: List[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if block and line.startswith((" ", "\t")):
            block.append(line.strip())  # a folded ">-" or "|" value continues on indented lines
            found[block[0]] = " ".join(block[1:])
            continue
        block = []
        match = _FIELD.match(line)
        if match:
            value = match.group(2).strip()
            found[match.group(1)] = "" if value in {">", ">-", "|", "|-"} else value.strip("'\"")
            block = [match.group(1)] if value in {">", ">-", "|", "|-"} else []
    return found


def screen(text: str) -> List[str]:
    flags = [name for name, pattern in FLAGS.items() if pattern.search(text)]
    return flags + (["hidden_characters"] if HIDDEN.search(text) else [])


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _head(checkout: Path) -> str:
    return subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()


def _skill_id(name: str, owner_repo: str, taken: Dict[str, str]) -> str:
    """The folder name, or the repository name in front when another source holds it."""
    source = f"https://github.com/{owner_repo}"
    if taken.get(name, source) == source:
        return name
    return f"{owner_repo.split('/')[1].lower()}-{name}"


def _licence_name(checkout: Path) -> str:
    try:
        head = next(checkout.glob("LICEN[CS]E*")).read_text(encoding="utf-8", errors="replace")[:400]
    except StopIteration:
        return "unknown"
    for marker, name in (("Apache License", "Apache-2.0"), ("Apache 2.0 License", "Apache-2.0"),
                         ("MIT License", "MIT"), ("unlicense", "Unlicense")):
        if marker.lower() in head.lower():
            return name
    return "see LICENSE"


def _copy_references(folder: Path, vendor_dir: str, catalog: dict, entry: dict, row: Dict[str, object]) -> None:
    """Text references the SKILL.md points to; each one screened, scripts never copied."""
    skipped: List[str] = []
    for path in sorted((folder / "references").rglob("*.md")) if (folder / "references").is_dir() else []:
        name = path.relative_to(folder).as_posix()
        data = path.read_bytes()
        if screen(data.decode("utf-8", errors="replace")) or len(data) > MAX_BYTES:
            skipped.append(name)
            continue
        target = ROOT / vendor_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entry["resources"][name] = f"{vendor_dir}/{name}"
        catalog["files"][f"{vendor_dir}/{name}"] = _sha(target)
    row["references"] = len(entry["resources"]) - 1
    if skipped:
        row["references_skipped"] = skipped


def _one_skill(folder: Path, checkout: Path, spec: Tuple[str, str, str], catalog: dict,
               taken: Dict[str, str], options: Dict[str, object]) -> Dict[str, object]:
    owner_repo, commit, _ = spec
    text_bytes = (folder / "SKILL.md").read_bytes()
    text = text_bytes.decode("utf-8", errors="replace")
    meta = front_matter(text)
    inside = folder.relative_to(checkout).as_posix()
    # A SKILL.md at the repository root is named by its own front matter.
    name = re.sub(r"[^a-z0-9-]+", "-", meta.get("name", "").lower()).strip("-") if inside == "." else folder.name
    skill_id = _skill_id(name or owner_repo.split("/")[1].lower(), owner_repo, taken)
    row: Dict[str, object] = {"id": skill_id, "source": owner_repo, "description": meta.get("description", ""),
                              "bytes": len(text_bytes),
                              "extra_files": sorted(p.name for p in folder.iterdir() if p.name != "SKILL.md")}
    flags = screen(text) + (["too_large"] if len(text_bytes) > MAX_BYTES else [])
    if skill_id in taken:
        return {**row, "status": "already_in_hub"}
    if flags:
        return {**row, "status": "excluded", "flags": flags}
    vendor_dir = f"skills/vendor/{owner_repo}" + ("" if inside == "." else f"/{inside}")
    target = ROOT / vendor_dir / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(text_bytes)
    catalog["files"][f"{vendor_dir}/SKILL.md"] = _sha(target)
    entry = {
        "id": skill_id, "source": f"https://github.com/{owner_repo}", "commit": commit,
        "source_path": inside, "license": options["licence"], "mode": "reference_only",
        "agents": [], "resources": {"SKILL.md": f"{vendor_dir}/SKILL.md"}, "summary": meta.get("description", "")[:300],
        "review": REVIEW.format(date=options["date"]),
    }
    if skill_id in options["with_references"]:
        _copy_references(folder, vendor_dir, catalog, entry, row)
    catalog["skills"].append(entry)
    taken[skill_id] = f"https://github.com/{owner_repo}"
    return {**row, "status": "added"}


def import_repo(checkouts: Path, spec: Tuple[str, str, str], catalog: dict, taken: Dict[str, str],
                options: Dict[str, object]) -> List[Dict[str, object]]:
    """``root`` is a folder of skill folders, or one skill folder (``.`` for the repository root)."""
    owner_repo, commit, root = spec
    checkout = checkouts / owner_repo.replace("/", "_")
    if _head(checkout) != commit:
        raise SystemExit(f"{owner_repo}: checkout is not at {commit}")
    licence = next(checkout.glob("LICEN[CS]E*"), None)
    vendor = ROOT / "skills" / "vendor" / owner_repo
    if licence is not None:
        vendor.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(licence, vendor / "LICENSE")
        catalog["files"][f"skills/vendor/{owner_repo}/LICENSE"] = _sha(vendor / "LICENSE")
    base = checkout / root
    folders = [base] if (base / "SKILL.md").is_file() else sorted(p.parent for p in base.glob("*/SKILL.md"))
    options = {**options, "licence": _licence_name(checkout)}
    return [_one_skill(folder, checkout, spec, catalog, taken, options) for folder in folders]


def main(argv: List[str]) -> int:
    if len(argv) < 4:
        print(__doc__, file=sys.stderr)
        return 2
    checkouts, report_path = Path(argv[1]), Path(argv[2])
    specs = [raw for raw in argv[3:] if not raw.startswith("--with-references=")]
    wanted = {name for raw in argv[3:] if raw.startswith("--with-references=")
              for name in raw.split("=", 1)[1].split(",") if name}
    options: Dict[str, object] = {"date": datetime.now(timezone.utc).date().isoformat(), "with_references": wanted}
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    taken = {item["id"]: item["source"] for item in catalog["skills"]}
    report: List[Dict[str, object]] = []
    for raw in specs:
        owner_repo, _, rest = raw.partition("@")
        commit, _, root = rest.partition(":")
        report += import_repo(checkouts, (owner_repo, commit, root or "skills"), catalog, taken, options)
    catalog["files"] = dict(sorted(catalog["files"].items()))
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    counts: Dict[str, int] = {}
    for row in report:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    print(json.dumps(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
