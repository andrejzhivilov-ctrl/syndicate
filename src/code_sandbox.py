"""The agents' ``run_python`` tool: code runs in the isolated sandbox, never here (19.11.2026).

``deploy/sandbox`` is a separate container on the internal network: no secrets, no Vault, no internet.
An agent sends code and, optionally, datasets it fetched before (``market_data`` keeps them on the
server by id) or small text files; it gets stdout, stderr and the files the code made. Images and
tables it made go to the agent's own Obsidian folder when asked (``save_to``).
"""
from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from src.data_paths import ensure_dir

SANDBOX_URL = os.environ.get("EVA_SANDBOX_URL", "http://code-sandbox:8080")
MAX_CODE_CHARS = 30_000
MAX_DATASETS = 5
MAX_OUTPUT_TO_AGENT = 8_000
SAVE_TYPES = frozenset({".png", ".svg", ".csv", ".xlsx", ".md", ".json", ".txt"})


def dataset_dir() -> Path:
    return ensure_dir("market_data")


def _datasets(names: List[str]) -> Dict[str, str]:
    files = {}
    for name in names[:MAX_DATASETS]:
        path = dataset_dir() / f"{name}.csv"
        if path.is_file():
            files[path.name] = path.read_text(encoding="utf-8")
    return files


def _save(made: Dict[str, str], save_to: Optional[Path], vault_root: Optional[Path]) -> List[str]:
    if save_to is None or vault_root is None:
        return []
    save_to.mkdir(parents=True, exist_ok=True)
    saved = []
    for name, data in made.items():
        if Path(name).suffix.lower() in SAVE_TYPES:
            target = save_to / name
            target.write_bytes(base64.b64decode(data))
            saved.append(target.relative_to(vault_root).as_posix())
    return saved


async def run(code: str, datasets: Optional[List[str]] = None, timeout: int = 60, *, save_to: Optional[Path] = None,
              vault_root: Optional[Path] = None, transport: Any = None) -> Dict[str, Any]:
    if not code.strip() or len(code) > MAX_CODE_CHARS:
        return {"status": "error", "error": "empty_or_too_long", "max_chars": MAX_CODE_CHARS}
    files = _datasets(list(datasets or []))
    missing = [name for name in datasets or [] if f"{name}.csv" not in files]
    try:
        async with httpx.AsyncClient(timeout=timeout + 30, transport=transport) as client:
            reply = await client.post(f"{SANDBOX_URL}/run", json={"code": code, "files": files, "timeout": timeout})
        reply.raise_for_status()
        result = reply.json()
    except (httpx.HTTPError, ValueError) as exc:
        return {"status": "unavailable", "reason": f"sandbox_unreachable: {type(exc).__name__}"}
    made = result.pop("files", {}) or {}
    saved = _save(made, save_to, vault_root)
    result["stdout"] = str(result.get("stdout") or "")[-MAX_OUTPUT_TO_AGENT:]
    result["stderr"] = str(result.get("stderr") or "")[-MAX_OUTPUT_TO_AGENT // 2:]
    result["files_made"] = sorted(made)
    if saved:
        result["saved"] = saved
    if missing:
        result["datasets_missing"] = missing
    return result
