#!/usr/bin/env python3
"""Print Architect deployment snapshot. Does not activate the profile."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.agents.architect_ready import architect_readiness  # noqa: E402


def main() -> int:
    snapshot = architect_readiness()
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    if snapshot.get("grants_empty") is not True:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
