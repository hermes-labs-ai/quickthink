#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_LOG = Path("docs/agent-comms/log.jsonl")
DEFAULT_VIEW = Path("docs/agent-comms/THREAD.md")


@dataclass
class Entry:
    timestamp: str
    agent: str
    status: str
    last_action: str
    notes: str
    questions: list[str]
    files: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "agent": self.agent,
            "status": self.status,
            "last_action": self.last_action,
            "notes": self.notes,
            "questions": self.questions,
            "files": self.files,
        }


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid jsonl line {idx}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"invalid jsonl line {idx}: expected object")
            entries.append(value)
    return entries


def append_entry(path: Path, entry: Entry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.to_dict(), ensure_ascii=True) + "\n")


def render_markdown(entries: list[dict[str, Any]], view_path: Path, limit: int) -> None:
    view_path.parent.mkdir(parents=True, exist_ok=True)
    selected = entries[-limit:] if limit > 0 else entries
    lines: list[str] = [
        "# Agent Thread",
        "",
        "Append-only coordination log for parallel agents.",
        "",
        "## Recent Updates",
        "",
    ]

    if not selected:
        lines.append("No updates yet.")
    else:
        for idx, item in enumerate(reversed(selected), 1):
            ts = str(item.get("timestamp", ""))
            agent = str(item.get("agent", "unknown"))
            status = str(item.get("status", ""))
            last_action = str(item.get("last_action", ""))
            notes = str(item.get("notes", ""))
            questions = item.get("questions", [])
            files = item.get("files", [])

            lines.append(f"### {idx}. {agent} ({status}) - {ts}")
            lines.append(f"- Last action: {last_action}")
            lines.append(f"- Notes: {notes}")
            if isinstance(files, list) and files:
                lines.append(f"- Files: {', '.join(str(f) for f in files)}")
            if isinstance(questions, list) and questions:
                lines.append(f"- Open questions: {' | '.join(str(q) for q in questions)}")
            lines.append("")

    view_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_post(args: argparse.Namespace) -> int:
    questions = [q.strip() for q in args.questions if q.strip()]
    files = [f.strip() for f in args.files if f.strip()]
    entry = Entry(
        timestamp=now_utc_iso(),
        agent=args.agent,
        status=args.status,
        last_action=args.last_action,
        notes=args.notes,
        questions=questions,
        files=files,
    )

    append_entry(args.log, entry)
    entries = read_entries(args.log)
    render_markdown(entries, args.view, args.limit)
    print("status=OK")
    print(f"log={args.log}")
    print(f"view={args.view}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    entries = read_entries(args.log)
    render_markdown(entries, args.view, args.limit)
    print("status=OK")
    print(f"entries={len(entries)}")
    print(f"view={args.view}")
    return 0


def cmd_tail(args: argparse.Namespace) -> int:
    entries = read_entries(args.log)
    for item in entries[-args.n :]:
        print(json.dumps(item, ensure_ascii=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-agent comms log helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--log", type=Path, default=DEFAULT_LOG, help="JSONL comms log")
    common.add_argument("--view", type=Path, default=DEFAULT_VIEW, help="Rendered markdown thread")
    common.add_argument("--limit", type=int, default=50, help="Max recent entries in rendered thread")

    post = sub.add_parser("post", parents=[common], help="Append a new agent update")
    post.add_argument("--agent", required=True, help="Agent name/id")
    post.add_argument("--status", required=True, choices=["in_progress", "blocked", "done"], help="Update status")
    post.add_argument("--last-action", required=True, help="Last concrete action taken")
    post.add_argument("--notes", required=True, help="Short note")
    post.add_argument("--questions", nargs="*", default=[], help="Open questions for other agents")
    post.add_argument("--files", nargs="*", default=[], help="Related files")
    post.set_defaults(func=cmd_post)

    render = sub.add_parser("render", parents=[common], help="Render markdown thread from log")
    render.set_defaults(func=cmd_render)

    tail = sub.add_parser("tail", help="Print latest JSONL entries")
    tail.add_argument("--log", type=Path, default=DEFAULT_LOG, help="JSONL comms log")
    tail.add_argument("-n", type=int, default=10, help="Number of entries")
    tail.set_defaults(func=cmd_tail)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
