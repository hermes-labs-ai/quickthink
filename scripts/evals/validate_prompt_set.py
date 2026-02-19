#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_KEYS = {
    "prompt_id",
    "group",
    "prompt",
    "expected_rubric",
    "pass_fail_checklist",
}
GROUPS = {
    "reasoning": ("R", 30),
    "structured_output": ("S", 30),
    "instruction_constraints": ("I", 30),
    "multi_turn_continuity": ("M", 30),
}
ID_RE = re.compile(r"^[RSIM]\d{3}$")


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(8192)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def validate(rows: list[dict[str, Any]], strict_counts: bool) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    group_counts: Counter[str] = Counter()

    for idx, row in enumerate(rows, 1):
        missing = REQUIRED_KEYS - row.keys()
        if missing:
            errors.append(f"row {idx}: missing keys {sorted(missing)}")
            continue

        prompt_id = str(row["prompt_id"]).strip()
        group = str(row["group"]).strip()
        prompt = str(row["prompt"]).strip()
        rubric = str(row["expected_rubric"]).strip()
        checklist = row["pass_fail_checklist"]

        if not ID_RE.match(prompt_id):
            errors.append(f"row {idx}: invalid prompt_id format '{prompt_id}'")
        if prompt_id in seen_ids:
            errors.append(f"row {idx}: duplicate prompt_id '{prompt_id}'")
        seen_ids.add(prompt_id)

        if group not in GROUPS:
            errors.append(f"row {idx}: invalid group '{group}'")
        else:
            prefix, _ = GROUPS[group]
            if not prompt_id.startswith(prefix):
                errors.append(f"row {idx}: group '{group}' expects prompt_id prefix '{prefix}'")
            group_counts[group] += 1

        if len(prompt) < 20:
            errors.append(f"row {idx}: prompt too short")
        if len(rubric) < 20:
            errors.append(f"row {idx}: expected_rubric too short")

        if not isinstance(checklist, list):
            errors.append(f"row {idx}: pass_fail_checklist must be a list")
        else:
            if len(checklist) < 2:
                errors.append(f"row {idx}: pass_fail_checklist must have at least 2 items")
            for item_idx, item in enumerate(checklist, 1):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"row {idx}: checklist item {item_idx} must be non-empty string")

    if strict_counts:
        for group, (_, expected) in GROUPS.items():
            actual = group_counts[group]
            if actual != expected:
                errors.append(f"group '{group}' count mismatch: expected {expected}, got {actual}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate quickthink eval prompt_set JSONL")
    parser.add_argument(
        "--path",
        default="docs/evals/prompt_set.jsonl",
        help="Path to prompt_set.jsonl",
    )
    parser.add_argument(
        "--no-strict-counts",
        action="store_true",
        help="Disable strict 30-per-group validation",
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

    errors = validate(rows, strict_counts=not args.no_strict_counts)
    digest = sha256_file(path)

    print(f"file={path}")
    print(f"rows={len(rows)}")
    print(f"sha256={digest}")

    if errors:
        print("status=FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("status=OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
