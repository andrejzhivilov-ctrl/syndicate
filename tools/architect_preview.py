#!/usr/bin/env python3
"""Print a local mermaid preview of an n8n JSON file. Does not call n8n."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.agents.architect import n8n_builder  # noqa: E402
from src.agents.architect_preview import build_preview  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) >= 2:
        raw = Path(argv[1]).read_text(encoding="utf-8")
        workflow = json.loads(raw)
    else:
        workflow = n8n_builder.build_workflow(name="architect-preview-demo", trigger="manual")
    preview = build_preview(workflow)
    print(json.dumps(
        {
            "status": preview["status"],
            "active": preview["active"],
            "calls_n8n_api": preview["calls_n8n_api"],
            "lint_ok": preview["lint_ok"],
            "explanations": preview["explanations"],
            "mermaid": preview["mermaid"],
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0 if preview["active"] is False else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
