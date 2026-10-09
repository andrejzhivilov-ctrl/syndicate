"""Host-owned SkillSpector wrapper. Scans proposals; never installs skills."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping

from src.agents.marshal_access import load_marshal_manifest

_SECRET_SHAPES = (
    re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}"),
    re.compile(r"sk-(?:proj-|live-)?[A-Za-z0-9_-]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+"),
)

_STRIP_ENV = (
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "SKILLSPECTOR_PROVIDER",
    "SKILLSPECTOR_MODEL",
    "SKILLSPECTOR_COMPAT_API_KEY",
    "SKILLSPECTOR_COMPAT_BASE_URL",
    "NVIDIA_INFERENCE_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_ACCESS_KEY_ID",
    "GOOGLE_API_KEY",
)

_REMOTE_PREFIXES = ("http://", "https://", "git@", "ssh://", "github.com/")


def _redact(text: str) -> str:
    redacted = text
    for pattern in _SECRET_SHAPES:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _scan_config(manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    data = dict(manifest or load_marshal_manifest())
    block = data.get("skill_scan")
    return dict(block) if isinstance(block, dict) else {}


_REPO_ROOT = Path(__file__).resolve().parents[2]
_LOCAL_BIN = _REPO_ROOT / ".tools" / "skillspector" / "bin" / "skillspector"


def resolve_skillspector_binary(manifest: Mapping[str, Any] | None = None, which=shutil.which) -> str | None:
    env_bin = os.environ.get("MARSHAL_SKILLSPECTOR_BIN", "").strip()
    if env_bin and Path(env_bin).is_file():
        return env_bin
    if _LOCAL_BIN.is_file():
        return str(_LOCAL_BIN)
    cfg = _scan_config(manifest)
    found = which(str(cfg.get("binary") or "skillspector"))
    return found


def marshal_skill_scan_allowed(manifest: Mapping[str, Any] | None = None) -> bool:
    """Host CLI may run; this is not a Marshal capability grant."""
    cfg = _scan_config(manifest)
    if cfg.get("llm_pass") is True or cfg.get("installs_skills") is True:
        return False
    if cfg.get("mode") != "no_llm":
        return False
    if str(cfg.get("tool", "")) != "skillspector":
        return False
    return True


def _scrubbed_env() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key not in _STRIP_ENV}
    env["SKILLSPECTOR_PROVIDER"] = ""
    return env


def _local_path(target: str | Path) -> Path | None:
    raw = str(target).strip()
    if not raw:
        return None
    lowered = raw.lower()
    if lowered.startswith(_REMOTE_PREFIXES) or "://" in raw:
        return None
    path = Path(raw).expanduser()
    if not path.exists():
        return None
    return path.resolve()


def _parse_report(stdout: str) -> tuple[int | None, int]:
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        return None, 0
    score = None
    for key in ("risk_score", "score", "risk"):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            score = int(value)
            break
    findings = payload.get("findings") if isinstance(payload.get("findings"), list) else []
    return score, len(findings)


def _unavailable(base: dict[str, Any], error: str, path: str | None = None) -> dict[str, Any]:
    result = {**base, "status": "scan_unavailable", "error": error, "recommendation": "unknown"}
    if path:
        result["path"] = path
    return result


def scan_skill_proposal(
    target: str | Path,
    *,
    manifest: Mapping[str, Any] | None = None,
    runner=subprocess.run,
    which=shutil.which,
) -> dict[str, Any]:
    """Run SkillSpector --no-llm on a local skill path. Missing binary is not 'safe'."""
    base = {
        "agent": "marshal",
        "tool": "skillspector",
        "mode": "no_llm",
        "installs_skill": False,
        "llm_pass": False,
    }
    if not marshal_skill_scan_allowed(manifest):
        return {**base, "status": "denied", "error": "skill_scan_not_configured"}

    path = _local_path(target)
    if path is None:
        return {**base, "status": "denied", "error": "remote_or_missing_path"}

    resolved = resolve_skillspector_binary(manifest, which=which)
    if not resolved:
        return _unavailable(base, "skillspector_not_installed", str(path))

    command = [resolved, "scan", str(path), "--no-llm", "--format", "json"]
    try:
        completed = runner(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            env=_scrubbed_env(),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _unavailable(base, type(exc).__name__, str(path))

    score, findings_count = _parse_report(_redact(completed.stdout or ""))
    recommendation = "unknown"
    if isinstance(score, int):
        recommendation = "do_not_install" if score > 50 else "review"
    return {
        **base,
        "status": "scanned",
        "path": str(path),
        "risk_score": score,
        "findings_count": findings_count,
        "recommendation": recommendation,
        "returncode": completed.returncode,
        "stderr_redacted": _redact(completed.stderr or "")[:2000],
    }
