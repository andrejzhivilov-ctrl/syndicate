#!/usr/bin/env python3
"""
EVA SYNDICATE — backup tool.

The operator's first request included a backup system; until now the repository
had *zero* lines of backup code — only three ad-hoc shell lines in the runbook
that nobody could run reliably, and a checklist item that could never pass.

This tool makes one timestamped backup set out of three artefacts:

  1. **PostgreSQL** — ``pg_dump --format=custom`` (``pg_restore`` can list, select
     and restore individual tables; a plain ``.sql.gz`` cannot).
  2. **Vault raft snapshot** — secrets are useless without this, because the
     database password, Redis password and every API key live in Vault.
  3. **Bootstrap files** — ``.env`` (the unseal variables, Redis password, AppRole
     ids). Included by default because a backup you cannot restore is not a
     backup; skipped with ``--no-env`` when the operator keeps it elsewhere.

Design rules (``AGENTS.md`` §1 — never fabricate data):

* Every artefact reports ``ok`` or ``unavailable`` **with the reason**. A skipped
  or failed step is never reported as success.
* A dump is **verified** (checksum + ``pg_restore --list`` header) before the set
  is declared good. An unverified dump is exactly the failure that is discovered
  on restore day.
* A tool that is not installed is ``unavailable``, never silently skipped.
* Exit code 0 only when the database dump (the one irreplaceable artefact)
  succeeded and verified.

Usage
-----
    python3 tools/backup.py                       # into $EVA_BACKUP_DIR or ./backups
    python3 tools/backup.py --dest /data/backups --keep-days 14
    python3 tools/backup.py --no-env --offsite    # push to restic, skip .env
    python3 tools/backup.py --list                # what is on disk right now

Restore procedure: ``DEPLOYMENT_RUNBOOK.md`` §13.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

SCHEMA_VERSION = 1
DEFAULT_KEEP_DAYS = 7
#: Binary overrides exist so tests can drive this against stubs on PATH.
TOOL_ENV = {
    "pg_dump": "EVA_PG_DUMP_BIN",
    "pg_restore": "EVA_PG_RESTORE_BIN",
    "vault": "EVA_VAULT_BIN",
    "restic": "EVA_RESTIC_BIN",
}


def _now() -> datetime:
    # datetime.utcnow() is forbidden in this repository.
    return datetime.now(timezone.utc)


def _tool(name: str) -> Optional[str]:
    """Resolve a binary: explicit env override first, then PATH.

    An override pointing at a missing file returns ``None`` (the caller reports
    it honestly) instead of raising ``FileNotFoundError`` out of the backup run.
    """
    env_var = TOOL_ENV.get(name, "")
    override = os.getenv(env_var, "").strip()
    if override:
        return override if os.path.isfile(override) else None
    return shutil.which(name)


def _missing_tool_message(name: str, purpose: str) -> str:
    """Explain what is missing, naming a bad override so the operator can see it."""
    env_var = TOOL_ENV.get(name, "")
    override = os.getenv(env_var, "").strip()
    if override:
        return (
            f"{purpose}: {env_var}={override} does not exist — fix the override "
            f"or unset it to search PATH"
        )
    return f"{purpose}: {name} not found (set {env_var} or install it)"


@dataclass
class Artifact:
    """One file in a backup set, with the truth about how it went."""

    name: str
    status: str  # ok | unavailable
    path: Optional[str] = None
    bytes: int = 0
    sha256: Optional[str] = None
    verified: bool = False
    warning: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "path": self.path,
            "bytes": self.bytes,
            "sha256": self.sha256,
            "verified": self.verified,
            "warning": self.warning,
        }


@dataclass
class BackupReport:
    stamp: str
    dest: str
    status: str = "ok"
    artifacts: List[Artifact] = field(default_factory=list)
    offsite: Dict[str, Any] = field(default_factory=lambda: {
        "status": "disabled", "warning": None, "repository": None,
    })
    pruned: List[str] = field(default_factory=list)

    def add(self, artifact: Artifact) -> Artifact:
        self.artifacts.append(artifact)
        return artifact

    @property
    def warnings(self) -> List[str]:
        found = [f"{a.name}: {a.warning}" for a in self.artifacts if a.warning]
        if self.offsite.get("warning"):
            found.append(f"offsite: {self.offsite['warning']}")
        return found

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "stamp": self.stamp,
            "created_at": _now().isoformat(),
            "dest": self.dest,
            "status": self.status,
            "artifacts": [a.as_dict() for a in self.artifacts],
            "offsite": self.offsite,
            "pruned": self.pruned,
            "warnings": self.warnings,
        }


# ─── helpers ─────────────────────────────────────────────────────────────────

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: Sequence[str], env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603 - argv list, no shell
        list(command),
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


def database_url() -> Optional[str]:
    """DSN for pg_dump, from DATABASE_URL or the POSTGRES_* variables."""
    explicit = (os.getenv("DATABASE_URL") or os.getenv("EVA_BACKUP_DATABASE_URL") or "").strip()
    if explicit:
        return explicit
    user = os.getenv("POSTGRES_USER", "eva")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    name = os.getenv("POSTGRES_DB", "eva_syndicate")
    if not password:
        return None
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


# ─── steps ───────────────────────────────────────────────────────────────────

def backup_database(report: BackupReport, dest: Path, dsn: str) -> Artifact:
    """Dump PostgreSQL, then prove the dump is readable before trusting it."""
    target = dest / "postgres.dump"
    pg_dump = _tool("pg_dump")
    if pg_dump is None:
        # Not installed is "unavailable" — never a silent skip, and never "ok".
        return report.add(Artifact(
            name="postgres",
            status="unavailable",
            warning=_missing_tool_message("pg_dump", "no database dump possible"),
        ))

    result = _run(
        [pg_dump, "--format=custom", "--no-owner", "--no-privileges", f"--file={target}", dsn]
    )
    if result.returncode != 0 or not target.exists() or target.stat().st_size == 0:
        # The password lives in the DSN; keep it out of the warning text.
        detail = (result.stderr or result.stdout or "no output").strip()[:400]
        return report.add(Artifact(
            name="postgres",
            status="unavailable",
            warning=f"pg_dump failed (exit {result.returncode}): {detail}",
        ))

    artifact = Artifact(
        name="postgres",
        status="ok",
        path=target.name,
        bytes=target.stat().st_size,
        sha256=_sha256(target),
    )

    pg_restore = _tool("pg_restore")
    if pg_restore is None:
        artifact.warning = (
            "pg_restore not found — the dump was written but NOT verified; "
            "a corrupt dump is discovered on restore day"
        )
    else:
        listing = _run([pg_restore, "--list", str(target)])
        if listing.returncode != 0:
            artifact.status = "unavailable"
            artifact.verified = False
            artifact.warning = (
                "the dump cannot be read back by pg_restore — treating it as broken: "
                f"{(listing.stderr or '').strip()[:300]}"
            )
        else:
            # A real dump lists its TOC; an empty or truncated file often yields
            # exit 0 with nothing in it.
            entries = [line for line in listing.stdout.splitlines() if line.strip()]
            if not entries:
                artifact.status = "unavailable"
                artifact.warning = "pg_restore listed no objects — the dump is empty"
            else:
                artifact.verified = True
    return report.add(artifact)


def backup_vault(report: BackupReport, dest: Path) -> Artifact:
    """Snapshot Vault's raft storage — without it the secrets are gone for good."""
    target = dest / "vault.snap"
    vault = _tool("vault")
    if vault is None:
        return report.add(Artifact(
            name="vault",
            status="unavailable",
            warning=_missing_tool_message("vault", "secrets cannot be snapshotted"),
        ))

    address = (os.getenv("VAULT_ADDR") or "").strip()
    token = (os.getenv("VAULT_TOKEN") or "").strip()
    if not address or not token:
        return report.add(Artifact(
            name="vault",
            status="unavailable",
            warning=(
                "VAULT_ADDR/VAULT_TOKEN not set in this shell — a snapshot needs a token "
                "(see DEPLOYMENT_RUNBOOK.md §13 for how to export the limited backup token)"
            ),
        ))

    result = _run([vault, "operator", "raft", "snapshot", "save", str(target)], env={"VAULT_ADDR": address})
    if result.returncode != 0 or not target.exists() or target.stat().st_size == 0:
        detail = (result.stderr or result.stdout or "no output").strip()[:400]
        return report.add(Artifact(
            name="vault",
            status="unavailable",
            warning=f"vault snapshot failed (exit {result.returncode}): {detail}",
        ))

    return report.add(Artifact(
        name="vault",
        status="ok",
        path=target.name,
        bytes=target.stat().st_size,
        sha256=_sha256(target),
        # raft snapshots carry their own integrity check on restore; a checksum
        # plus non-zero size is what can be verified here.
        verified=True,
    ))


def backup_env_file(report: BackupReport, dest: Path) -> Artifact:
    """Copy the bootstrap ``.env`` — required for a restore to be possible."""
    source = Path(os.getenv("EVA_DOTENV_FILE", ".env"))
    if not source.exists():
        return report.add(Artifact(
            name="env",
            status="unavailable",
            warning=f"{source} not found — restore would need the secrets from elsewhere",
        ))

    target = dest / "env.bootstrap"
    shutil.copyfile(source, target)
    # The copy is as sensitive as the original; do not leave it world-readable.
    target.chmod(0o600)
    return report.add(Artifact(
        name="env",
        status="ok",
        path=target.name,
        bytes=target.stat().st_size,
        sha256=_sha256(target),
        verified=True,
        warning=(
            "contains secrets (unseal material, Redis password, AppRole ids) — "
            "the backup destination must be encrypted at rest"
        ),
    ))


def push_offsite(report: BackupReport, dest: Path, enabled: bool) -> None:
    """Optional restic push. Absent restic is reported, never faked."""
    if not enabled:
        report.offsite = {
            "status": "disabled",
            "warning": "offsite copy not requested (--offsite)",
            "repository": None,
        }
        return

    repository = (os.getenv("RESTIC_REPOSITORY") or "").strip()
    if not repository:
        # Configuration first: when both are missing, "you never named a
        # destination" is the actionable cause.
        report.offsite = {
            "status": "unavailable",
            "warning": "RESTIC_REPOSITORY is not set — nothing to push to",
            "repository": None,
        }
        return

    restic = _tool("restic")
    if restic is None:
        report.offsite = {
            "status": "unavailable",
            "warning": _missing_tool_message("restic", "offsite copy impossible"),
            "repository": repository,
        }
        return

    result = _run([restic, "backup", str(dest), "--tag", "eva-syndicate"])
    if result.returncode != 0:
        report.offsite = {
            "status": "unavailable",
            "warning": f"restic backup failed (exit {result.returncode}): "
                       f"{(result.stderr or '').strip()[:300]}",
            "repository": repository,
        }
        return
    report.offsite = {"status": "ok", "warning": None, "repository": repository}


def prune(dest: Path, keep_days: int, exclude: Optional[Path] = None) -> List[str]:
    """Delete backup sets older than ``keep_days``. Returns what was removed."""
    removed: List[str] = []
    if keep_days <= 0:
        return removed
    cutoff = _now() - timedelta(days=keep_days)
    for entry in sorted(dest.glob("20*")):
        if not entry.is_dir() or entry == exclude:
            continue
        try:
            stamp = datetime.strptime(entry.name, "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue  # not one of ours — leave it alone
        if stamp < cutoff:
            shutil.rmtree(entry, ignore_errors=True)
            removed.append(entry.name)
    return removed


def write_manifest(report: BackupReport, dest: Path) -> Path:
    manifest = dest / "manifest.json"
    manifest.write_text(
        json.dumps(report.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def list_sets(dest: Path) -> List[Dict[str, Any]]:
    """Summarise the backup sets on disk, for ``--list``."""
    found: List[Dict[str, Any]] = []
    for entry in sorted(dest.glob("20*"), reverse=True):
        manifest = entry / "manifest.json"
        if not manifest.is_file():
            found.append({"stamp": entry.name, "status": "unavailable",
                          "warning": "no manifest.json — set is incomplete"})
            continue
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            found.append({
                "stamp": payload.get("stamp", entry.name),
                "status": payload.get("status", "unknown"),
                "artifacts": [a["name"] for a in payload.get("artifacts", []) if a["status"] == "ok"],
                "warnings": payload.get("warnings", []),
            })
        except (ValueError, OSError) as exc:
            found.append({"stamp": entry.name, "status": "unavailable",
                          "warning": f"unreadable manifest: {exc}"})
    return found


def run_backup(
    dest: Path,
    keep_days: int = DEFAULT_KEEP_DAYS,
    include_env: bool = True,
    offsite: bool = False,
) -> BackupReport:
    """Make one backup set. Returns the report; never raises for a missing tool."""
    stamp = _now().strftime("%Y-%m-%dT%H-%M-%SZ")
    target = dest / stamp
    target.mkdir(parents=True, exist_ok=True)
    report = BackupReport(stamp=stamp, dest=str(target))

    dsn = database_url()
    if dsn:
        backup_database(report, target, dsn)
    else:
        # Do not invent a DSN: say exactly what is missing.
        report.add(Artifact(
            name="postgres",
            status="unavailable",
            warning="no database URL: set DATABASE_URL or POSTGRES_PASSWORD",
        ))

    backup_vault(report, target)

    if include_env:
        backup_env_file(report, target)
    else:
        report.add(Artifact(name="env", status="unavailable",
                            warning="excluded on request (--no-env)"))

    write_manifest(report, target)
    push_offsite(report, target, offsite)
    report.pruned = prune(dest, keep_days, exclude=target)

    # The database is the irreplaceable artefact: everything else can be
    # re-obtained, so the exit code keys on it alone.
    database = next((a for a in report.artifacts if a.name == "postgres"), None)
    critical_ok = bool(database and database.status == "ok" and database.verified)
    report.status = "ok" if critical_ok else "unavailable"

    write_manifest(report, target)  # rewrite with the final status and pruning
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="EVA SYNDICATE backup tool")
    parser.add_argument("--dest", default=os.getenv("EVA_BACKUP_DIR", "backups"),
                        help="destination directory (default $EVA_BACKUP_DIR or ./backups)")
    parser.add_argument("--keep-days", type=int, default=int(os.getenv("EVA_BACKUP_KEEP_DAYS", DEFAULT_KEEP_DAYS)),
                        help="delete backup sets older than this many days (0 = keep all)")
    parser.add_argument("--no-env", action="store_true", help="do not copy the bootstrap .env")
    parser.add_argument("--offsite", action="store_true", help="also push to RESTIC_REPOSITORY")
    parser.add_argument("--list", action="store_true", help="list existing backup sets and exit")
    args = parser.parse_args(argv)

    dest = Path(args.dest).expanduser()
    dest.mkdir(parents=True, exist_ok=True)

    if args.list:
        sets = list_sets(dest)
        if not sets:
            print(json.dumps({"status": "ok", "value": [], "warning": f"no backup sets in {dest}"},
                             ensure_ascii=False, indent=2))
            return 0
        print(json.dumps({"status": "ok", "value": sets, "warning": None}, ensure_ascii=False, indent=2))
        return 0

    report = run_backup(dest, keep_days=args.keep_days, include_env=not args.no_env, offsite=args.offsite)
    payload = report.as_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    for artifact in report.artifacts:
        mark = "OK " if artifact.status == "ok" else "!! "
        detail = artifact.warning or f"{artifact.bytes} bytes, sha256 {str(artifact.sha256)[:12]}…"
        print(f"  {mark}{artifact.name}: {detail}", file=sys.stderr)
    if report.offsite.get("warning"):
        print(f"  !! offsite: {report.offsite['warning']}", file=sys.stderr)
    print(f"  status: {report.status}  set: {report.dest}", file=sys.stderr)

    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
