#!/usr/bin/env python3
"""Owner-run offline studio CLI. Does not activate agents or connect Google APIs."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.antigravity.history import HistoryIndex  # noqa: E402
from src.antigravity.local_builders import landing, poster, video  # noqa: E402
from src.antigravity.studio import TASK_KINDS, Studio  # noqa: E402
from src.antigravity.workspace import StudioError, Workspace  # noqa: E402


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    commands.add_parser("init")
    create = commands.add_parser("task")
    create.add_argument("kind", choices=sorted(TASK_KINDS))
    create.add_argument("--brief-file", required=True, help="UTF-8 path relative to private workspace")
    packet = commands.add_parser("packet")
    packet.add_argument("task_id")
    packet.add_argument("--operator-reviewed", action="store_true")
    receive = commands.add_parser("receive")
    receive.add_argument("task_id")
    receive.add_argument("inbox_file")
    site = commands.add_parser("landing")
    site.add_argument("--title", required=True)
    site.add_argument("--description", required=True)
    image = commands.add_parser("poster")
    image.add_argument("--title", required=True)
    clip = commands.add_parser("video")
    clip.add_argument("frame")
    clip.add_argument("--seconds", type=int, default=5)
    ingest = commands.add_parser("history-ingest")
    ingest.add_argument("inbox_file")
    ingest.add_argument("--operator-reviewed", action="store_true")
    search = commands.add_parser("history-search")
    search.add_argument("query")
    commands.add_parser("audit-report")
    return root


def run(args: argparse.Namespace) -> dict:
    if args.command == "status":
        return {
            "agent_activation": "prepared_not_enabled", "mode": "google_subscription_manual",
            "subscription_verified": False, "google_login": "owner_in_official_product",
            "api_calls": "not_implemented", "github_access": False, "billing_connected": False,
            "local_tools": ["task", "packet", "receive", "landing", "poster", "video", "history-ingest", "history-search"],
        }
    ws = Workspace()
    return _execute(args, ws)


def _execute(args: argparse.Namespace, ws: Workspace) -> dict:
    studio = Studio(ws)
    if args.command == "init":
        return {"status": "private_workspace_ready", "root": str(ws.root)}
    if args.command == "task":
        task = studio.create(args.kind, ws.read(args.brief_file).decode("utf-8"))
        return {"status": task["status"], "task_id": task["id"]}
    if args.command == "packet":
        path = studio.packet(args.task_id, operator_reviewed=args.operator_reviewed)
        return {"status": "prepared_for_manual_use_not_sent", "path": path}
    if args.command == "receive":
        return studio.receive(args.task_id, args.inbox_file)
    if args.command == "landing":
        return {"status": "created_static_draft", "path": landing(ws, args.title, args.description)}
    if args.command == "poster":
        return {"status": "created_deterministic_png", "path": poster(ws, args.title)}
    if args.command == "video":
        return video(ws, args.frame, seconds=args.seconds)
    if args.command == "history-ingest":
        return HistoryIndex(ws).ingest(args.inbox_file, operator_reviewed=args.operator_reviewed)
    if args.command == "history-search":
        return HistoryIndex(ws).search(args.query)
    # Owner manually includes this content in Eva's 21:00 report; no background delivery.
    records = [json.loads(ws.read(f"audit/{p.name}")) for p in sorted(ws.path("audit").glob("*.json"))]
    return {"status": "local_report_not_delivered_to_eva", "events": records}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run(args)
    except StudioError as exc:
        print(json.dumps({"status": "rejected", "reason": str(exc)}))
        return 2
    except (OSError, UnicodeError, sqlite3.Error, ValueError):
        print(json.dumps({"status": "unavailable", "reason": "local_operation_failed"}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "unavailable" else 0


if __name__ == "__main__":
    raise SystemExit(main())
