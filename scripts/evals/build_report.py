#!/usr/bin/env python3
from __future__ import annotations

"""
Legacy report helper for smoke/demo flows.

Canonical reporting pipeline lives under scripts/eval_harness/report_suite.py.
"""

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    lo = int(math.floor(rank))
    hi = int(math.ceil(rank))
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (rank - lo)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def latency_summary(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, float]]:
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        buckets[(str(row["model"]), str(row["mode"]))].append(float(row["total_latency_ms"]))

    out: dict[tuple[str, str], dict[str, float]] = {}
    for key, vals in buckets.items():
        out[key] = {
            "count": float(len(vals)),
            "avg_ms": sum(vals) / len(vals),
            "p50_ms": percentile(vals, 0.50),
            "p95_ms": percentile(vals, 0.95),
        }
    return out


def judge_summary(judges: list[dict[str, Any]]) -> tuple[dict[tuple[str, str], dict[str, float]], dict[tuple[str, str], Counter[str]]]:
    stats: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"wins": 0.0, "losses": 0.0, "ties": 0.0, "total": 0.0})
    failures: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)

    for row in judges:
        model = str(row["model"])
        group = str(row.get("group", "unknown"))
        mode_a = str(row["mode_a"])
        mode_b = str(row["mode_b"])
        winner = str(row["winner"]).upper()

        key_a = (model, f"{mode_a}_vs_{mode_b}")
        key_b = (model, f"{mode_b}_vs_{mode_a}")

        stats[key_a]["total"] += 1
        stats[key_b]["total"] += 1

        if winner == "A":
            stats[key_a]["wins"] += 1
            stats[key_b]["losses"] += 1
            failures[(model, mode_b)][group] += 1
        elif winner == "B":
            stats[key_b]["wins"] += 1
            stats[key_a]["losses"] += 1
            failures[(model, mode_a)][group] += 1
        else:
            stats[key_a]["ties"] += 1
            stats[key_b]["ties"] += 1

    for row in stats.values():
        total = row["total"] or 1.0
        non_tie = max(1.0, row["wins"] + row["losses"])
        row["raw_win_rate"] = row["wins"] / total
        row["non_tie_win_rate"] = row["wins"] / non_tie

    return stats, failures


def to_markdown(
    report_ts: str,
    lat: dict[tuple[str, str], dict[str, float]],
    judge_stats: dict[tuple[str, str], dict[str, float]],
    failures: dict[tuple[str, str], Counter[str]],
) -> str:
    lines: list[str] = [
        "# QuickThink Eval Report",
        "",
        f"Generated: {report_ts}",
        "",
        "## Latency Summary",
        "",
        "| Model | Mode | Count | Avg ms | P50 ms | P95 ms |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for (model, mode), vals in sorted(lat.items()):
        lines.append(
            f"| {model} | {mode} | {int(vals['count'])} | {vals['avg_ms']:.2f} | {vals['p50_ms']:.2f} | {vals['p95_ms']:.2f} |"
        )

    lines.extend(["", "## Win-Rate Summary", ""])
    if not judge_stats:
        lines.append("No judge data provided. Win-rate unavailable.")
    else:
        lines.append("| Model | Pairing | Raw Win Rate | Non-Tie Win Rate |")
        lines.append("|---|---|---:|---:|")
        for (model, pairing), vals in sorted(judge_stats.items()):
            lines.append(
                f"| {model} | {pairing} | {vals['raw_win_rate']*100:.1f}% | {vals['non_tie_win_rate']*100:.1f}% |"
            )

    lines.extend(["", "## Per-Group Failures", ""])
    if not failures:
        lines.append("No judge data provided. Failure breakdown unavailable.")
    else:
        lines.append("| Model | Mode | Group | Loss Count |")
        lines.append("|---|---|---|---:|")
        for (model, mode), counts in sorted(failures.items()):
            for group, count in counts.most_common():
                lines.append(f"| {model} | {mode} | {group} | {count} |")

    return "\n".join(lines) + "\n"


def to_html(markdown_text: str) -> str:
    escaped = (
        markdown_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>QuickThink Eval Report</title>"
        "<style>body{font-family:ui-monospace,Menlo,monospace;margin:2rem;line-height:1.4;}"
        "pre{white-space:pre-wrap;background:#f6f8fa;padding:1rem;border-radius:8px;}</style>"
        "</head><body><h1>QuickThink Eval Report</h1><pre>"
        + escaped
        + "</pre></body></html>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build markdown/html eval report")
    parser.add_argument("--results", required=True)
    parser.add_argument("--judge", default="")
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--out-html", required=True)
    args = parser.parse_args()

    report_ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    results = load_jsonl(Path(args.results))
    lat = latency_summary(results)

    judges: list[dict[str, Any]] = []
    if args.judge:
        judge_path = Path(args.judge)
        if judge_path.exists():
            judges = load_jsonl(judge_path)

    judge_stats, failures = judge_summary(judges)
    md = to_markdown(report_ts, lat, judge_stats, failures)
    html = to_html(md)

    out_md = Path(args.out_md)
    out_html = Path(args.out_html)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md, encoding="utf-8")
    out_html.write_text(html, encoding="utf-8")

    print(f"status=OK md={out_md} html={out_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
