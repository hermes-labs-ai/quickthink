#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def load_prompt_set(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def select_balanced(rows: list[dict[str, Any]], per_group: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["group"])].append(row)

    selected: list[dict[str, Any]] = []
    for group in sorted(grouped.keys()):
        selected.extend(grouped[group][:per_group])
    return selected


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def model_supports_thinking(model: str) -> bool:
    model_l = model.lower()
    return model_l.startswith(("qwen3", "deepseek-r1", "deepseek-v3", "gpt-oss"))


def write_experiment_readme(exp_dir: Path, meta: dict[str, Any]) -> None:
    lines = [
        "# Frozen Experiment",
        "",
        f"Experiment ID: `{meta['experiment_id']}`",
        f"Created (UTC): `{meta['created_utc']}`",
        "",
        "## Goal",
        "Run a frozen mode comparison on a balanced mixed prompt slice.",
        "",
        "## Scope",
        f"- Models: {', '.join(meta['models'])}",
        f"- Runs per prompt/mode: {meta['runs']}",
        f"- Prompts per group: {meta['per_group']}",
        f"- Total prompts: {meta['prompt_count']}",
        f"- Modes: {', '.join(meta['modes'])}",
        "",
        "## Files",
        "- `prompt_subset.jsonl`: frozen prompt slice for this experiment",
        "- `run_results.jsonl`: raw model outputs + timings",
        "- `run_manifest.json`: reproducibility metadata",
        "- `judged_results.jsonl`: judged rows",
        "- `report_summary.json`: machine-readable summary",
        "- `report_summary.md`: readable summary",
        "",
        "## Notes",
        "- This folder is local/private by default (`experiments-local/` is gitignored).",
        "- Safe to copy as a self-contained artifact for your own storage.",
    ]
    (exp_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen tri-mode experiment in isolated folder")
    parser.add_argument("--name", default="tri-mode-mixed")
    parser.add_argument("--prompt-set", default="docs/evals/prompt_set.jsonl")
    parser.add_argument("--base-dir", default="experiments-local")
    parser.add_argument("--per-group", type=int, default=3)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--models", nargs="*", default=["qwen2.5:1.5b", "mistral:7b", "qwen3:4b", "gemma3:27b"])
    parser.add_argument("--modes", nargs="*", default=["direct", "lite", "two_pass"])
    parser.add_argument(
        "--include-thinking-baseline",
        action="store_true",
        help="Add direct_think mode when any selected model supports thinking",
    )
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--judge-backend", choices=["rule", "ollama"], default="rule")
    parser.add_argument("--judge-model", default="gemma3:27b")
    args = parser.parse_args()

    experiment_id = f"{now_tag()}-{args.name}"
    exp_dir = Path(args.base_dir) / experiment_id
    exp_dir.mkdir(parents=True, exist_ok=True)

    source_rows = load_prompt_set(Path(args.prompt_set))
    subset = select_balanced(source_rows, per_group=args.per_group)
    subset_path = exp_dir / "prompt_subset.jsonl"
    with subset_path.open("w", encoding="utf-8") as fh:
        for row in subset:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")

    run_results = exp_dir / "run_results.jsonl"
    run_manifest = exp_dir / "run_manifest.json"
    judged = exp_dir / "judged_results.jsonl"
    summary_json = exp_dir / "report_summary.json"
    summary_md = exp_dir / "report_summary.md"
    modes = list(args.modes)
    if args.include_thinking_baseline and any(model_supports_thinking(m) for m in args.models):
        if "direct_think" not in modes:
            modes.append("direct_think")

    meta = {
        "experiment_id": experiment_id,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "models": list(args.models),
        "runs": args.runs,
        "per_group": args.per_group,
        "prompt_count": len(subset),
        "modes": modes,
        "judge_backend": args.judge_backend,
        "judge_model": args.judge_model,
        "ollama_url": args.ollama_url,
    }
    (exp_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    write_experiment_readme(exp_dir, meta)

    run(
        [
            "python3",
            "scripts/eval_harness/run_suite.py",
            "--prompt-set",
            str(subset_path),
            "--out",
            str(run_results),
            "--manifest-out",
            str(run_manifest),
            "--models",
            *args.models,
            "--modes",
            *modes,
            "--runs",
            str(args.runs),
            "--ollama-url",
            args.ollama_url,
        ]
    )

    run(
        [
            "python3",
            "scripts/eval_harness/judge_suite.py",
            "--prompt-set",
            str(subset_path),
            "--results",
            str(run_results),
            "--out",
            str(judged),
            "--backend",
            args.judge_backend,
            "--judge-model",
            args.judge_model,
            "--ollama-url",
            args.ollama_url,
        ]
    )

    run(["python3", "scripts/eval_harness/validate_judged_results.py", "--path", str(judged)])

    run(
        [
            "python3",
            "scripts/eval_harness/report_suite.py",
            "--runs",
            str(run_results),
            "--judged",
            str(judged),
            "--out-json",
            str(summary_json),
            "--out-md",
            str(summary_md),
        ]
    )

    print(f"status=OK experiment_dir={exp_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
