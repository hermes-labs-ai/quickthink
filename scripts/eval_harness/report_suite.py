#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return math.nan
    arr = sorted(values)
    idx = (len(arr) - 1) * pct
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return arr[lo]
    return arr[lo] + (arr[hi] - arr[lo]) * (idx - lo)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def build_latency_index(run_rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[float]]:
    index: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in run_rows:
        key = (str(row["model"]), str(row["mode"]))
        index[key].append(float(row.get("total_latency_ms", 0.0)))
    return index


def build_score_index(judge_rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[float]]:
    index: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in judge_rows:
        key = (str(row["model"]), str(row["mode"]))
        index[key].append(float(row.get("total_score", 0.0)))
    return index


def pairwise_win_rate(
    judge_rows: list[dict[str, Any]],
    model: str,
    lhs_mode: str,
    rhs_mode: str,
) -> dict[str, float]:
    lhs: dict[tuple[str, int], float] = {}
    rhs: dict[tuple[str, int], float] = {}

    for row in judge_rows:
        if str(row.get("model")) != model:
            continue
        key = (str(row.get("prompt_id")), int(row.get("run_index", 0)))
        mode = str(row.get("mode"))
        score = float(row.get("total_score", 0.0))
        if mode == lhs_mode:
            lhs[key] = score
        elif mode == rhs_mode:
            rhs[key] = score

    wins = 0
    losses = 0
    ties = 0
    for key, lhs_score in lhs.items():
        if key not in rhs:
            continue
        rhs_score = rhs[key]
        if lhs_score > rhs_score:
            wins += 1
        elif lhs_score < rhs_score:
            losses += 1
        else:
            ties += 1

    total = wins + losses + ties
    non_ties = wins + losses
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "raw_win_rate": (wins / total) if total else math.nan,
        "non_tie_win_rate": (wins / non_ties) if non_ties else math.nan,
    }


def group_win_rate(
    judge_rows: list[dict[str, Any]],
    model: str,
    lhs_mode: str,
    rhs_mode: str,
) -> dict[str, dict[str, float]]:
    rows_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in judge_rows:
        if str(row.get("model")) == model:
            rows_by_group[str(row.get("group"))].append(row)

    out: dict[str, dict[str, float]] = {}
    for group, rows in rows_by_group.items():
        out[group] = pairwise_win_rate(rows, model, lhs_mode, rhs_mode)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Build eval summary report")
    parser.add_argument("--runs", default="docs/evals/results/run_results.jsonl")
    parser.add_argument("--judged", default="docs/evals/results/judged_results.jsonl")
    parser.add_argument("--out-json", default="docs/evals/results/report_summary.json")
    parser.add_argument("--out-md", default="docs/evals/results/report_summary.md")
    parser.add_argument("--out-html", default="")
    args = parser.parse_args()

    run_rows = load_jsonl(Path(args.runs))
    judge_rows = load_jsonl(Path(args.judged))
    if not run_rows:
        raise SystemExit("no run rows found")
    if not judge_rows:
        raise SystemExit("no judged rows found")

    models = sorted({str(r["model"]) for r in run_rows})
    modes = sorted({str(r["mode"]) for r in run_rows})

    latency_index = build_latency_index(run_rows)
    score_index = build_score_index(judge_rows)

    summary: dict[str, Any] = {
        "models": {},
        "pairs": {},
    }

    lines: list[str] = []
    lines.append("# Eval Summary")
    lines.append("")

    for model in models:
        lines.append(f"## {model}")
        lines.append("")
        lines.append("| mode | avg_score | p50_ms | p95_ms | avg_total_ms |")
        lines.append("|---|---:|---:|---:|---:|")

        model_entry: dict[str, Any] = {"modes": {}}
        for mode in modes:
            lat = latency_index.get((model, mode), [])
            scores = score_index.get((model, mode), [])
            avg_score = mean(scores)
            p50 = percentile(lat, 0.5)
            p95 = percentile(lat, 0.95)
            avg_ms = mean(lat)
            lines.append(f"| {mode} | {avg_score:.2f} | {p50:.2f} | {p95:.2f} | {avg_ms:.2f} |")
            model_entry["modes"][mode] = {
                "avg_score": avg_score,
                "p50_ms": p50,
                "p95_ms": p95,
                "avg_total_ms": avg_ms,
                "rows": len(lat),
            }

        summary["models"][model] = model_entry
        lines.append("")

        pair_defs = [("lite", "direct"), ("two_pass", "direct"), ("lite", "two_pass")]
        for lhs, rhs in pair_defs:
            if lhs not in modes or rhs not in modes:
                continue
            pair_key = f"{model}:{lhs}_vs_{rhs}"
            overall = pairwise_win_rate(judge_rows, model, lhs, rhs)
            by_group = group_win_rate(judge_rows, model, lhs, rhs)
            summary["pairs"][pair_key] = {
                "overall": overall,
                "by_group": by_group,
            }

            lines.append(f"### {lhs} vs {rhs}")
            lines.append("")
            lines.append(
                "- overall: wins={wins} losses={losses} ties={ties} raw={raw:.3f} non_tie={non_tie:.3f}".format(
                    wins=int(overall["wins"]),
                    losses=int(overall["losses"]),
                    ties=int(overall["ties"]),
                    raw=float(overall["raw_win_rate"]),
                    non_tie=float(overall["non_tie_win_rate"]),
                )
            )
            for group, stats in sorted(by_group.items()):
                lines.append(
                    "- {group}: wins={wins} losses={losses} ties={ties} raw={raw:.3f} non_tie={non_tie:.3f}".format(
                        group=group,
                        wins=int(stats["wins"]),
                        losses=int(stats["losses"]),
                        ties=int(stats["ties"]),
                        raw=float(stats["raw_win_rate"]),
                        non_tie=float(stats["non_tie_win_rate"]),
                    )
                )
            lines.append("")

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if args.out_html:
        out_html = Path(args.out_html)
        out_html.parent.mkdir(parents=True, exist_ok=True)
        escaped = (
            out_md.read_text(encoding="utf-8")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>QuickThink Eval Summary</title>"
            "<style>body{font-family:ui-monospace,Menlo,monospace;margin:2rem;line-height:1.4;}"
            "pre{white-space:pre-wrap;background:#f6f8fa;padding:1rem;border-radius:8px;}</style>"
            "</head><body><h1>QuickThink Eval Summary</h1><pre>"
            + escaped
            + "</pre></body></html>"
        )
        out_html.write_text(html, encoding="utf-8")

    print(f"wrote report json: {out_json}")
    print(f"wrote report md: {out_md}")
    if args.out_html:
        print(f"wrote report html: {args.out_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
