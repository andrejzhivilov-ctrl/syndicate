#!/usr/bin/env python3
"""Export the live FastAPI schema as the client contract.

The PC/mobile client (``apps/``) must be generated against a contract that is
produced from the running code, never hand-written. A hand-written contract
silently drifts, and drift shows up as a runtime 422 in the app — the most
expensive possible place to discover it.

Usage
-----
    python tools/export_openapi.py                 # write apps/shared/api-contract.yaml
    python tools/export_openapi.py --check         # exit 1 if the committed file is stale
    python tools/export_openapi.py --stdout        # print instead of writing

Exit codes
----------
    0  written / up to date
    1  --check found drift (the committed contract is stale)
    2  the schema could not be generated
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "apps" / "shared" / "api-contract.yaml"

sys.path.insert(0, str(REPO_ROOT))


def _banner() -> str:
    return (
        "# ============================================================\n"
        "# EVA SYNDICATE — client API contract\n"
        "#\n"
        "# GENERATED FILE — DO NOT EDIT BY HAND.\n"
        "# Source of truth: deploy/runtime/agent_runner.py (FastAPI app).\n"
        "# Regenerate with:  python tools/export_openapi.py\n"
        "# Verify in CI with: python tools/export_openapi.py --check\n"
        "# ============================================================\n"
    )


def build_schema() -> dict:
    """Import the app and produce its OpenAPI document."""
    from deploy.runtime.agent_runner import app  # noqa: PLC0415

    schema = app.openapi()
    if not isinstance(schema, dict) or not schema.get("paths"):
        raise RuntimeError("generated OpenAPI schema is empty — nothing to export")
    return schema


def canonical_bytes(schema: dict) -> bytes:
    return json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")


def render(schema: dict, out_path: Path) -> str:
    """YAML when PyYAML is available, JSON otherwise (never silently skip)."""
    digest = hashlib.sha256(canonical_bytes(schema)).hexdigest()
    header = (
        f"{_banner()}"
        f"#\n"
        f"# contract_sha256: {digest}\n"
        f"# api_version:     {schema.get('info', {}).get('version', 'unknown')}\n"
        f"# paths:           {len(schema.get('paths', {}))}\n"
        f"#\n"
    )
    try:
        import yaml  # noqa: PLC0415

        body = yaml.safe_dump(schema, sort_keys=True, allow_unicode=True, default_flow_style=False)
        return header + "---\n" + body
    except ImportError:
        sys.stderr.write(
            "WARNING: PyYAML not installed — writing JSON instead. "
            "Install pyyaml to get the canonical .yaml contract.\n"
        )
        return header + json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"output path (default: {DEFAULT_OUT})")
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed contract is stale")
    parser.add_argument("--stdout", action="store_true", help="print the contract instead of writing it")
    args = parser.parse_args()

    try:
        schema = build_schema()
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"ERROR: could not generate OpenAPI schema: {exc}\n")
        return 2

    text = render(schema, args.out)

    if args.stdout:
        sys.stdout.write(text)
        return 0

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current == text:
            print(f"OK  contract up to date: {args.out.relative_to(REPO_ROOT)}")
            return 0
        print(f"STALE  {args.out.relative_to(REPO_ROOT)}")
        print("       Run: python tools/export_openapi.py  and commit the result.")
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    rel = args.out.relative_to(REPO_ROOT)
    print(f"WROTE {rel}  ({len(schema.get('paths', {}))} paths, "
          f"{hashlib.sha256(canonical_bytes(schema)).hexdigest()[:12]}…)")

    # Convenience: keep a JSON twin next to it for tooling that wants JSON.
    json_twin = args.out.with_suffix(".json")
    json_twin.write_text(json.dumps(schema, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"WROTE {json_twin.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
