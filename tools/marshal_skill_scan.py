#!/usr/bin/env python3
"""Scan a local skill directory for a Marshal HITL proposal. Does not install it."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.agents.marshal_skill_scan import scan_skill_proposal  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/marshal_skill_scan.py <local-skill-path>", file=sys.stderr)
        return 2
    result = scan_skill_proposal(argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") != "scanned":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
