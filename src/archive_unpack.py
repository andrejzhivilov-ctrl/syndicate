"""Archives in the knowledge channel are opened, not stored as blobs (Andrii, 19.11.2026).

An archive (zip, rar, 7z, tar, gz…) that reaches an agent's materials is unpacked into a sibling folder
«<name> (архів)»; each file inside then gets its own Markdown card like any other material. The archive
itself gets a card listing what was inside, and its original goes to Drive like every original.

Guards (an archive is untrusted data): the listing is read first (``lsar -j``); an entry with an absolute
path or «..» is refused, as are passwords, more than ``MAX_ENTRIES`` files, more than ``MAX_UNPACKED_BYTES``
or more than half the free disk; nested archives are opened at most ``MAX_DEPTH`` levels deep; links are
removed after unpacking. Nothing is guessed: a refusal is a reason, and the archive stays as it is.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List

ARCHIVES = frozenset({"zip", "rar", "7z", "tar", "gz", "tgz", "bz2", "xz", "tbz2", "txz"})
SUFFIX = " (архів)"
MAX_ENTRIES = 5_000
MAX_UNPACKED_BYTES = 30 * 1024 ** 3
MAX_DEPTH = 2
TIMEOUT = 1_800
#: Reasons worth another try on a later run (the tool arrives with an image rebuild).
LATER = frozenset({"archive_tool_missing"})


def is_archive(path: Path) -> bool:
    return path.suffix.lower().lstrip(".") in ARCHIVES


def _depth(path: Path) -> int:
    return sum(1 for part in path.parts if part.endswith(SUFFIX))


def _unsafe(name: str) -> bool:
    pure = PurePosixPath(name.replace("\\", "/"))
    return pure.is_absolute() or ".." in pure.parts or (len(name) > 1 and name[1] == ":")


def listing(path: Path) -> Dict[str, Any]:
    """What is inside, from ``lsar -j`` (nothing is unpacked)."""
    tool = shutil.which("lsar")
    if tool is None:
        return {"status": "unavailable", "reason": "archive_tool_missing"}
    try:
        done = subprocess.run([tool, "-j", str(path)], capture_output=True, timeout=120, check=False)
        data = json.loads(done.stdout.decode("utf-8", errors="replace") or "{}")
    except (subprocess.TimeoutExpired, ValueError):
        return {"status": "unavailable", "reason": "damaged_archive"}
    entries = data.get("lsarContents") if isinstance(data, dict) else None
    if done.returncode != 0 or not isinstance(entries, list):
        return {"status": "unavailable", "reason": "damaged_archive"}
    files = [e for e in entries if isinstance(e, dict) and not e.get("XADIsDirectory")]
    names = [str(e.get("XADFileName", "")) for e in files]
    return {"status": "ok", "names": names, "bytes": sum(int(e.get("XADFileSize") or 0) for e in files),
            "encrypted": bool(data.get("lsarEncrypted"))
            or any(e.get("XADIsEncrypted") for e in entries if isinstance(e, dict))}


def _refusal(path: Path, info: Dict[str, Any]) -> str:
    if info["encrypted"]:
        return "password_protected"
    if any(_unsafe(name) for name in info["names"]):
        return "unsafe_paths"
    if len(info["names"]) > MAX_ENTRIES:
        return "too_many_files"
    if info["bytes"] > MAX_UNPACKED_BYTES or info["bytes"] * 2 > shutil.disk_usage(path.parent).free:
        return "archive_too_large"
    return ""


def _free(target: Path) -> Path:
    if not target.exists():
        return target
    for number in range(2, 1000):
        candidate = target.with_name(f"{target.name} {number}")
        if not candidate.exists():
            return candidate
    raise OSError("no free name")


def _clean(folder: Path) -> List[Path]:
    """Drop links (never followed) and anything that escaped; return the unpacked files."""
    root = folder.resolve()
    files = []
    for item in sorted(folder.rglob("*")):
        if item.is_symlink():
            item.unlink()
        elif item.is_file() and root in item.resolve().parents:
            files.append(item)
    return files


def unpack(path: Path) -> Dict[str, Any]:
    """Unpack one archive next to itself; the Markdown body says what came out, or why nothing did."""
    if _depth(path) >= MAX_DEPTH:
        return {"status": "unavailable", "reason": "nested_too_deep"}
    tool = shutil.which("unar")
    info = listing(path)
    if tool is None or info["status"] != "ok":
        return {"status": "unavailable", "reason": info.get("reason") or "archive_tool_missing"}
    refusal = _refusal(path, info)
    if refusal:
        return {"status": "unavailable", "reason": refusal}
    target = _free(path.with_name(path.name.rsplit(".", 1)[0] + SUFFIX))
    try:
        done = subprocess.run([tool, "-q", "-no-recursion", "-no-directory", "-o", str(target), str(path)],
                              capture_output=True, timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        return {"status": "unavailable", "reason": "unpack_timeout", "folder": str(target)}
    files = _clean(target) if target.is_dir() else []
    if done.returncode != 0 or not files:
        return {"status": "unavailable", "reason": "unpack_failed", "folder": str(target)}
    shown = [str(f.relative_to(target)) for f in files[:200]]
    more = f"\n- … ще {len(files) - 200}" if len(files) > 200 else ""
    text = (f"Архів розпаковано в теку «{target.name}»: файлів {len(files)}, "
            f"{info['bytes'] / 1024 / 1024:.1f} МБ. Кожен файл має свою картку поруч із ним.\n\n"
            + "\n".join(f"- {name}" for name in shown) + more)
    return {"status": "ok", "text": text, "by": "unar", "folder": str(target), "files": len(files)}


def sample(path: Path) -> str:
    """The names inside, so Eva can route an archive by what it holds, not only by its own name."""
    info = listing(path)
    if info["status"] != "ok":
        return ""
    return "Вміст архіву: " + ", ".join(info["names"][:40])
