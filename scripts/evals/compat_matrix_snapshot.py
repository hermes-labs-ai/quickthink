#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from quickthink.config import PRESET_PROFILES, SUPPORTED_MODELS, QuickThinkConfig
from quickthink.engine import QuickThinkEngine

PROMPTS = [
    "In exactly five words, summarize tiny-model reliability.",
    "Return minified JSON: {\"risk\":\"x\",\"mitigation\":\"y\",\"owner\":\"z\"}.",
    "In exactly six words, compare direct vs scaffolded output.",
]


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


def run_mode(prompt: str, model: str, mode: str, preset: str, ollama_url: str) -> float:
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config.apply_preset(preset)
    config.request_timeout_s = 480.0
    if mode == "direct":
        config.mode = "lite"
        config.adaptive_routing = False
        config.bypass_short_prompts = True
        config.bypass_char_threshold = 100_000
    else:
        config.mode = mode
    return QuickThinkEngine(config).run(prompt).total_latency_ms


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate compatibility matrix snapshot")
    parser.add_argument("--out-json", default="docs/compatibility/snapshots/latest.json")
    parser.add_argument("--out-md", default="docs/compatibility_matrix.md")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--max-prompts", type=int, default=3)
    parser.add_argument("--preset", default="balanced", choices=sorted(PRESET_PROFILES.keys()))
    args = parser.parse_args()

    prompt_set = PROMPTS[: max(1, min(args.max_prompts, len(PROMPTS)))]
    rows = []
    for model in SUPPORTED_MODELS:
        direct_vals: list[float] = []
        lite_vals: list[float] = []
        two_vals: list[float] = []
        for prompt in prompt_set:
            for _ in range(args.runs):
                direct_vals.append(run_mode(prompt, model, "direct", args.preset, args.ollama_url))
                lite_vals.append(run_mode(prompt, model, "lite", args.preset, args.ollama_url))
                two_vals.append(run_mode(prompt, model, "two_pass", args.preset, args.ollama_url))

        direct_p50 = percentile(direct_vals, 0.5)
        lite_p50 = percentile(lite_vals, 0.5)
        lite_p95 = percentile(lite_vals, 0.95)
        two_p50 = percentile(two_vals, 0.5)

        lite_overhead_p50 = lite_p50 - direct_p50
        lite_status = "PASS" if lite_overhead_p50 <= 80 and lite_p95 - percentile(direct_vals, 0.95) <= 200 else "WARN"

        rows.append(
            {
                "model": model,
                "preset": args.preset,
                "direct_p50_ms": round(direct_p50, 2),
                "lite_p50_ms": round(lite_p50, 2),
                "lite_p95_ms": round(lite_p95, 2),
                "two_pass_p50_ms": round(two_p50, 2),
                "lite_overhead_p50_ms": round(lite_overhead_p50, 2),
                "support_status": lite_status,
            }
        )

    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "generated_at": ts,
        "preset": args.preset,
        "runs_per_prompt": args.runs,
        "prompts": prompt_set,
        "models": rows,
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Compatibility Matrix",
        "",
        f"Generated: {ts}",
        "",
        "Supported models: `qwen2.5:1.5b`, `mistral:7b`, `gemma3:27b`.",
        "",
        "| Model | Preset | Direct p50 | Lite p50 | Lite p95 | Lite overhead p50 | Two-pass p50 | Status |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['preset']} | {row['direct_p50_ms']:.2f} | {row['lite_p50_ms']:.2f} | {row['lite_p95_ms']:.2f} | {row['lite_overhead_p50_ms']:.2f} | {row['two_pass_p50_ms']:.2f} | {row['support_status']} |"
        )

    lines.extend([
        "",
        "Notes:",
        "- Status PASS means lite overhead meets target thresholds on snapshot prompts.",
        "- Re-generate with: `python3 scripts/evals/compat_matrix_snapshot.py`.",
    ])

    out_md = Path(args.out_md)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"status=OK json={out_json} md={out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
