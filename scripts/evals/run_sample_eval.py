#!/usr/bin/env python3
from __future__ import annotations

"""
Smoke/demo runner.

Canonical batch evaluation pipeline lives under scripts/eval_harness/.
Use this script for quick local checks only.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quickthink.config import PRESET_PROFILES, SUPPORTED_MODELS, QuickThinkConfig
from quickthink.engine import QuickThinkEngine


def load_prompts(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sample_by_group(rows: list[dict[str, Any]], per_group: int) -> list[dict[str, Any]]:
    by_group: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_group.setdefault(str(row["group"]), []).append(row)

    selected: list[dict[str, Any]] = []
    for group in sorted(by_group.keys()):
        selected.extend(by_group[group][:per_group])
    return selected


def run_mode(prompt: str, model: str, ollama_url: str, mode: str, preset: str) -> dict[str, Any]:
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config.apply_preset(preset)

    if mode == "direct":
        config.mode = "lite"
        config.adaptive_routing = False
        config.bypass_short_prompts = True
        config.bypass_char_threshold = 100_000
    else:
        config.mode = mode

    result = QuickThinkEngine(config).run(prompt)
    return {
        "mode": mode,
        "answer": result.answer,
        "plan": result.plan,
        "plan_repaired": result.plan_repaired,
        "bypassed": result.bypassed,
        "route_score": result.route_score,
        "selected_plan_budget": result.selected_plan_budget,
        "plan_latency_ms": round(result.plan_latency_ms, 2),
        "answer_latency_ms": round(result.answer_latency_ms, 2),
        "total_latency_ms": round(result.total_latency_ms, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run quickthink sample eval suite")
    parser.add_argument("--prompt-set", default="docs/evals/prompt_set.jsonl")
    parser.add_argument("--out", default="docs/evals/results/sample-run.jsonl")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--per-group", type=int, default=2)
    parser.add_argument("--preset", default="balanced", choices=sorted(PRESET_PROFILES.keys()))
    parser.add_argument("--models", nargs="*", default=list(SUPPORTED_MODELS))
    args = parser.parse_args()

    prompts = load_prompts(Path(args.prompt_set))
    selected = sample_by_group(prompts, args.per_group)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    modes = ["direct", "lite", "two_pass"]

    with out_path.open("w", encoding="utf-8") as fh:
        for model in args.models:
            for row in selected:
                for run_idx in range(1, args.runs + 1):
                    for mode in modes:
                        result = run_mode(
                            prompt=str(row["prompt"]),
                            model=model,
                            ollama_url=args.ollama_url,
                            mode=mode,
                            preset=args.preset,
                        )
                        payload = {
                            "timestamp": now,
                            "model": model,
                            "preset": args.preset,
                            "mode": result["mode"],
                            "prompt_id": row["prompt_id"],
                            "group": row["group"],
                            "prompt": row["prompt"],
                            "run_index": run_idx,
                            "answer": result["answer"],
                            "plan": result["plan"],
                            "plan_repaired": result["plan_repaired"],
                            "bypassed": result["bypassed"],
                            "route_score": result["route_score"],
                            "selected_plan_budget": result["selected_plan_budget"],
                            "plan_latency_ms": result["plan_latency_ms"],
                            "answer_latency_ms": result["answer_latency_ms"],
                            "total_latency_ms": result["total_latency_ms"],
                        }
                        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")

    print(f"status=OK out={out_path}")
    print(f"prompts={len(selected)} models={len(args.models)} runs={args.runs} modes=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
