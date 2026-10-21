#!/usr/bin/env python3
"""
SYNDICATE — Antigravity Identity & Memory Export Engine.
Extracts and packages the complete Antigravity Assistant identity, episodic memory,
conversation transcripts, skills, rules, and configuration into a portable, verified archive.

Enables seamless migration to a Virtual Machine (Proxmox, WSL2, VPS, or dedicated laptop)
with zero loss of state, learned behaviors, or project context.

Usage:
    python tools/backup_antigravity_identity.py
    python tools/backup_antigravity_identity.py --dest /data/backups/antigravity
"""

from __future__ import annotations

import sys
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach(), errors="replace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach(), errors="replace")

import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent

# Standard Antigravity paths on host
USER_HOME = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "~"))).expanduser()
GLOBAL_CONFIG_DIR = USER_HOME / ".gemini" / "config"
ANTIGRAVITY_APP_DIR = USER_HOME / ".gemini" / "antigravity"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def create_antigravity_backup(dest_dir: Path, conversation_id: str | None = None) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _now_iso()
    archive_name = f"antigravity_identity_snapshot_{timestamp}.tar.gz"
    archive_path = dest_dir / archive_name
    manifest_path = dest_dir / f"antigravity_identity_snapshot_{timestamp}.manifest.json"

    print(f"📦 Packaging Antigravity Identity Snapshot: {archive_path}")

    files_collected: List[Dict[str, Any]] = []

    with tarfile.open(archive_path, "w:gz") as tar:
        # 1. Global config (~/.gemini/config: rules, skills)
        if GLOBAL_CONFIG_DIR.exists():
            print(f"  -> Adding Global Config: {GLOBAL_CONFIG_DIR}")
            tar.add(GLOBAL_CONFIG_DIR, arcname="gemini_config")

        # 2. Builtin skills / extensions if available
        builtin_skills = ANTIGRAVITY_APP_DIR / "builtin" / "skills"
        if builtin_skills.exists():
            print(f"  -> Adding Builtin Skills: {builtin_skills}")
            tar.add(builtin_skills, arcname="builtin_skills")

        # 3. Brain & Conversation Logs for specific conversation or all
        brain_dir = ANTIGRAVITY_APP_DIR / "brain"
        if brain_dir.exists():
            if conversation_id and (brain_dir / conversation_id).exists():
                conv_path = brain_dir / conversation_id
                print(f"  -> Adding Active Conversation Memory & Artifacts: {conv_path.name}")
                # Add transcripts
                logs_dir = conv_path / ".system_generated" / "logs"
                if logs_dir.exists():
                    tar.add(logs_dir, arcname=f"brain/{conversation_id}/logs")
                # Add root documentation and markdown artifacts
                for item in conv_path.iterdir():
                    if item.is_file() and item.suffix.lower() in (".md", ".json", ".html", ".pdf", ".txt"):
                        tar.add(item, arcname=f"brain/{conversation_id}/artifacts/{item.name}")
                # Add docs directory if present
                docs_dir = conv_path / "docs"
                if docs_dir.exists():
                    tar.add(docs_dir, arcname=f"brain/{conversation_id}/docs")
            else:
                # Add transcripts of active conversations
                for c_dir in brain_dir.iterdir():
                    if c_dir.is_dir() and not c_dir.name.startswith("."):
                        logs_dir = c_dir / ".system_generated" / "logs"
                        if logs_dir.exists():
                            tar.add(logs_dir, arcname=f"brain/{c_dir.name}/logs")

        # 4. Syndicate Repository Git State metadata
        git_dir = REPO_ROOT / ".git"
        if git_dir.exists():
            print("  -> Adding Git Commit Reference & HEAD")
            head_ref = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
            manifest_info = {
                "git_head": head_ref,
                "created_at": timestamp,
                "source_host": os.environ.get("COMPUTERNAME", "unknown"),
                "conversation_id": conversation_id,
            }
        else:
            manifest_info = {"created_at": timestamp}

    # Generate Manifest & Integrity Checksum
    archive_hash = _sha256(archive_path)
    manifest_data = {
        "schema_version": 1,
        "type": "antigravity_identity_snapshot",
        "timestamp": timestamp,
        "archive_file": archive_name,
        "sha256": archive_hash,
        "size_bytes": archive_path.stat().st_size,
        "metadata": manifest_info,
        "instructions": (
            "To restore on a new virtual machine or PC: "
            "run `python tools/restore_antigravity_identity.py --archive <path>`"
        ),
    }

    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Archive complete: {archive_path.stat().st_size / (1024*1024):.2f} MB (SHA256: {archive_hash[:16]}...)")
    print(f"📄 Manifest written: {manifest_path}")
    return archive_path


def main():
    parser = argparse.ArgumentParser(description="Backup Antigravity Identity & Memory")
    parser.add_argument("--dest", default=str(REPO_ROOT / "backups" / "antigravity"), help="Destination directory")
    parser.add_argument("--conversation-id", default=None, help="Specific conversation ID to snapshot")
    args = parser.parse_args()

    # Detect current conversation id from path if possible
    conv_id = args.conversation_id
    if not conv_id:
        match = [p for p in REPO_ROOT.parents if len(p.name) == 36 and "-" in p.name]
        if match:
            conv_id = match[0].name

    create_antigravity_backup(Path(args.dest), conv_id)


if __name__ == "__main__":
    main()
