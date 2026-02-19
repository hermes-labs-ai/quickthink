#!/usr/bin/env python3
from __future__ import annotations

"""
Legacy pairwise judge helper for smoke/demo flows.

Canonical judged pipeline lives under scripts/eval_harness/.
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quickthink.ollama_client import OllamaClient

_PAIRINGS = (("lite", "direct"), ("two_pass", "direct"), ("lite", "two_pass"))
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def load_results(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def extract_json(text: str) -> dict[str, Any]:
    match = _JSON_RE.search(text)
    if not match:
        return {"winner": "tie", "confidence": 0.0, "reason": "No parseable JSON from judge"}
    try:
        data = json.loads(match.group(0))
        if not isinstance(data, dict):
            raise ValueError("judge output not object")
    except Exception:
        return {"winner": "tie", "confidence": 0.0, "reason": "Invalid JSON from judge"}

    winner = str(data.get("winner", "tie")).strip().upper()
    if winner not in {"A", "B", "TIE"}:
        winner = "TIE"
    confidence = data.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    reason = str(data.get("reason", ""))[:400]
    return {"winner": winner, "confidence": confidence, "reason": reason}


def make_judge_prompt(task: str, answer_a: str, answer_b: str) -> str:
    return (
        "You are evaluating which answer better satisfies a user task.\n"
        "Use these criteria: correctness, constraint adherence, format validity, verbosity control.\n"
        "Return JSON only with keys: winner, confidence, reason.\n"
        "winner must be one of: A, B, TIE. confidence in [0,1].\n"
        "Do not add any other text.\n\n"
        f"Task:\n{task}\n\n"
        f"Answer A:\n{answer_a}\n\n"
        f"Answer B:\n{answer_b}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Pairwise judge quickthink eval outputs")
    parser.add_argument("--results", required=True, help="Input run results JSONL")
    parser.add_argument("--out", required=True, help="Output judge JSONL")
    parser.add_argument("--judge-model", default="gemma3:27b")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    args = parser.parse_args()

    rows = load_results(Path(args.results))
    grouped: dict[tuple[str, str, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        key = (str(row["model"]), str(row["prompt_id"]), int(row["run_index"]))
        grouped[key][str(row["mode"])] = row

    client = OllamaClient(args.ollama_url)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    with out_path.open("w", encoding="utf-8") as fh:
        for key, bucket in grouped.items():
            model, prompt_id, run_idx = key
            for mode_a, mode_b in _PAIRINGS:
                if mode_a not in bucket or mode_b not in bucket:
                    continue
                row_a = bucket[mode_a]
                row_b = bucket[mode_b]
                judge_prompt = make_judge_prompt(
                    str(row_a.get("prompt", row_a.get("prompt_id", ""))),
                    str(row_a.get("answer", "")),
                    str(row_b.get("answer", "")),
                )
                resp = client.generate(
                    model=args.judge_model,
                    prompt=judge_prompt,
                    temperature=0.0,
                    top_p=1.0,
                    max_tokens=256,
                )
                parsed = extract_json(str(resp.get("response", "")))
                payload = {
                    "timestamp": now,
                    "judge_model": args.judge_model,
                    "model": model,
                    "prompt_id": prompt_id,
                    "group": row_a.get("group"),
                    "run_index": run_idx,
                    "mode_a": mode_a,
                    "mode_b": mode_b,
                    "winner": parsed["winner"],
                    "confidence": parsed["confidence"],
                    "reason": parsed["reason"],
                }
                fh.write(json.dumps(payload, ensure_ascii=True) + "\n")

    print(f"status=OK out={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
