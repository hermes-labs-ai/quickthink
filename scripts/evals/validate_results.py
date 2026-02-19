#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

REQUIRED_FIELDS = {
    "timestamp",
    "model",
    "mode",
    "prompt_id",
    "group",
    "run_index",
    "answer",
    "plan_repaired",
    "bypassed",
    "route_score",
    "selected_plan_budget",
    "plan_latency_ms",
    "answer_latency_ms",
    "total_latency_ms",
}
ALLOWED_MODES = {"direct", "lite", "two_pass"}


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
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {lineno}: invalid JSON ({exc})") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {lineno}: top-level value must be an object")
            rows.append(value)
    return rows


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_keys: set[tuple[str, str, str, int]] = set()

    for idx, row in enumerate(rows, 1):
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            errors.append(f"row {idx}: missing keys {sorted(missing)}")
            continue

        mode = str(row["mode"]).strip()
        if mode not in ALLOWED_MODES:
            errors.append(f"row {idx}: invalid mode '{mode}'")

        key = (
            str(row["model"]),
            mode,
            str(row["prompt_id"]),
            int(row["run_index"]),
        )
        if key in seen_keys:
            errors.append(
                f"row {idx}: duplicate model/mode/prompt_id/run_index combination {key}"
            )
        seen_keys.add(key)

        for metric in ("plan_latency_ms", "answer_latency_ms", "total_latency_ms"):
            try:
                value = float(row[metric])
            except (TypeError, ValueError):
                errors.append(f"row {idx}: {metric} must be numeric")
                continue
            if value < 0:
                errors.append(f"row {idx}: {metric} must be >= 0")

    return errors


def summarize(rows: list[dict[str, Any]]) -> None:
    latencies: dict[str, list[float]] = defaultdict(list)
    by_mode: Counter[str] = Counter()
    by_model: Counter[str] = Counter()

    for row in rows:
        mode = str(row["mode"])
        model = str(row["model"])
        by_mode[mode] += 1
        by_model[model] += 1
        latencies[mode].append(float(row["total_latency_ms"]))

    print("summary:")
    print(f"- rows={len(rows)}")
    print(f"- models={dict(by_model)}")
    print(f"- modes={dict(by_mode)}")

    for mode in sorted(latencies.keys()):
        values = latencies[mode]
        print(
            "- mode={} p50_ms={:.2f} p95_ms={:.2f} avg_ms={:.2f}".format(
                mode,
                median(values),
                percentile(values, 0.95),
                sum(values) / len(values),
            )
        )


def check_coverage(
    rows: list[dict[str, Any]], expected_prompts: int, expected_runs: int, models: list[str]
) -> list[str]:
    errors: list[str] = []
    if expected_prompts <= 0 or expected_runs <= 0:
        return errors

    needed_modes = sorted(ALLOWED_MODES)
    coverage: dict[tuple[str, str], set[tuple[str, int]]] = defaultdict(set)
    for row in rows:
        coverage[(str(row["model"]), str(row["mode"]))].add(
            (str(row["prompt_id"]), int(row["run_index"]))
        )

    # Prompt IDs are category-based (R/S/I/M...), so we validate by slot counts.
    expected_slot_count = expected_prompts * expected_runs

    target_models = models if models else sorted({str(r["model"]) for r in rows})
    for model in target_models:
        for mode in needed_modes:
            actual = len(coverage[(model, mode)])
            if actual != expected_slot_count:
                errors.append(
                    f"coverage mismatch for model={model} mode={mode}: expected {expected_slot_count}, got {actual}"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate quickthink eval results JSONL")
    parser.add_argument("--path", required=True, help="Path to eval results JSONL")
    parser.add_argument("--expected-prompts", type=int, default=0, help="Expected unique prompt count")
    parser.add_argument("--expected-runs", type=int, default=0, help="Expected run count per prompt/mode")
    parser.add_argument(
        "--models",
        nargs="*",
        default=[],
        help="Optional explicit model list for coverage checks",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"error: file not found: {path}")
        return 2

    try:
        rows = load_jsonl(path)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    errors = validate_rows(rows)
    errors.extend(
        check_coverage(
            rows,
            expected_prompts=args.expected_prompts,
            expected_runs=args.expected_runs,
            models=args.models,
        )
    )

    if errors:
        print("status=FAILED")
        for err in errors:
            print(f"- {err}")
        summarize(rows)
        return 1

    print("status=OK")
    summarize(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
