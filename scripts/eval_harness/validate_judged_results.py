#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TOP_KEYS = {
    "timestamp",
    "model",
    "mode",
    "prompt_id",
    "group",
    "run_index",
    "answer",
    "scores",
    "total_score",
    "passed",
    "judge_backend",
    "judge_confidence",
    "judge_notes",
}
REQUIRED_SCORE_KEYS = {
    "correctness",
    "constraint_adherence",
    "format_validity",
    "verbosity_control",
}
ALLOWED_MODES = {"direct", "lite", "two_pass", "direct_think"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {lineno}: invalid JSON ({exc})") from exc
            if not isinstance(row, dict):
                raise ValueError(f"line {lineno}: top-level value must be object")
            rows.append(row)
    return rows


def validate_rows(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[tuple[str, str, str, int]] = set()

    for idx, row in enumerate(rows, 1):
        missing = REQUIRED_TOP_KEYS - set(row.keys())
        if missing:
            errors.append(f"row {idx}: missing keys {sorted(missing)}")
            continue

        mode = str(row.get("mode", "")).strip()
        if mode not in ALLOWED_MODES:
            errors.append(f"row {idx}: invalid mode '{mode}'")

        key = (
            str(row.get("model", "")),
            mode,
            str(row.get("prompt_id", "")),
            int(row.get("run_index", 0) or 0),
        )
        if key in seen:
            errors.append(f"row {idx}: duplicate model/mode/prompt_id/run_index {key}")
        seen.add(key)

        scores = row.get("scores", {})
        if not isinstance(scores, dict):
            errors.append(f"row {idx}: scores must be an object")
            continue
        missing_scores = REQUIRED_SCORE_KEYS - set(scores.keys())
        if missing_scores:
            errors.append(f"row {idx}: missing score keys {sorted(missing_scores)}")

        total = 0
        for score_key in REQUIRED_SCORE_KEYS:
            try:
                val = int(scores[score_key])
            except Exception:
                errors.append(f"row {idx}: score '{score_key}' must be int")
                continue
            if val < 0 or val > 2:
                errors.append(f"row {idx}: score '{score_key}' must be in [0,2]")
            total += val

        try:
            total_score = int(row.get("total_score", -1))
            if total_score != total:
                errors.append(f"row {idx}: total_score mismatch expected {total}, got {total_score}")
        except Exception:
            errors.append(f"row {idx}: total_score must be int")

        try:
            conf = float(row.get("judge_confidence", -1.0))
            if conf < 0.0 or conf > 1.0:
                errors.append(f"row {idx}: judge_confidence must be in [0,1]")
        except Exception:
            errors.append(f"row {idx}: judge_confidence must be numeric")

        if not isinstance(row.get("passed"), bool):
            errors.append(f"row {idx}: passed must be boolean")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate judged eval JSONL rows")
    parser.add_argument("--path", required=True, help="Path to judged results JSONL")
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
    if errors:
        print("status=FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("status=OK")
    print(f"rows={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
