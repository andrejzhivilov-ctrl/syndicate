#!/usr/bin/env python3
"""
SYNDICATE — Antigravity Identity & Memory Restore Engine.
Restores a packaged Antigravity snapshot onto a new Virtual Machine or computer,
re-instating global rules, skills, memory artifacts, and configuration.

Usage:
    python tools/restore_antigravity_identity.py --archive backups/antigravity/antigravity_identity_snapshot_xxx.tar.gz
"""

from __future__ import annotations

import sys
if sys.platform == "win32" and __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

USER_HOME = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "~"))).expanduser()
GLOBAL_CONFIG_DIR = USER_HOME / ".gemini" / "config"
ANTIGRAVITY_APP_DIR = USER_HOME / ".gemini" / "antigravity"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def restore_antigravity_backup(archive_path: Path, force: bool = False):
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    # Verify manifest if present
    manifest_candidate = archive_path.with_suffix("").with_suffix(".manifest.json")
    if manifest_candidate.exists():
        manifest = json.loads(manifest_candidate.read_text(encoding="utf-8"))
        expected_hash = manifest.get("sha256")
        if expected_hash:
            actual_hash = _sha256(archive_path)
            if actual_hash != expected_hash:
                raise ValueError(f"Integrity check failed! Expected {expected_hash}, got {actual_hash}")
            print(f"🔒 Checksum verified: {actual_hash[:16]}...")

    print(f"🚀 Restoring Antigravity Identity from: {archive_path}")

    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name.startswith("gemini_config"):
                sub_rel = member.name.replace("gemini_config", "").lstrip("/\\")
                target = GLOBAL_CONFIG_DIR / sub_rel
            elif member.name.startswith("builtin_skills"):
                sub_rel = member.name.replace("builtin_skills", "").lstrip("/\\")
                target = ANTIGRAVITY_APP_DIR / "builtin" / "skills" / sub_rel
            elif member.name.startswith("brain"):
                target = ANTIGRAVITY_APP_DIR / member.name
            else:
                continue

            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src_file, open(target, "wb") as dst_file:
                    shutil.copyfileobj(src_file, dst_file)

    print("🎉 Antigravity identity, rules, skills, and memory restored successfully!")
    print(f"   Config: {GLOBAL_CONFIG_DIR}")
    print(f"   App Dir: {ANTIGRAVITY_APP_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Restore Antigravity Identity & Memory")
    parser.add_argument("--archive", required=True, help="Path to .tar.gz snapshot")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files without prompting")
    args = parser.parse_args()

    restore_antigravity_backup(Path(args.archive), args.force)


if __name__ == "__main__":
    main()
