#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from time import sleep
from typing import Any

from quickthink import QuickThinkConfig, QuickThinkEngine


@dataclass
class Variant:
    name: str
    rules: str


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def model_supports_thinking(model: str) -> bool:
    model_l = model.lower()
    return model_l.startswith(("qwen3", "deepseek-r1", "deepseek-v3", "gpt-oss"))


def load_prompt_set(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_variants(path: Path, top_k: int) -> list[Variant]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    out = [Variant(name=str(r["name"]), rules=str(r["rules"])) for r in rows]
    if top_k > 0:
        out = out[:top_k]
    return out


def find_latest_pipeline1_variants(base_dir: Path) -> Path:
    runs_root = base_dir / "pipeline1-runs"
    candidates = sorted(runs_root.glob("*-pipeline1-cycle/selected_variants.json"))
    if not candidates:
        raise SystemExit(f"no pipeline1 variants found under {runs_root}")
    return candidates[-1]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def append_jsonl_row(fh: Any, row: dict[str, Any]) -> None:
    fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def row_key(row: dict[str, Any]) -> tuple[str, str, str, int]:
    return (
        str(row.get("model", "")),
        str(row.get("mode", "")),
        str(row.get("prompt_id", "")),
        int(row.get("run_index", 0)),
    )


def load_existing_row_keys(path: Path) -> set[tuple[str, str, str, int]]:
    keys: set[tuple[str, str, str, int]] = set()
    if not path.exists():
        return keys
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            keys.add(row_key(row))
    return keys


def load_existing_direct_rows(path: Path) -> dict[tuple[str, str, int], dict[str, Any]]:
    out: dict[tuple[str, str, int], dict[str, Any]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(row.get("mode", "")) != "direct":
                continue
            key = (str(row.get("model", "")), str(row.get("prompt_id", "")), int(row.get("run_index", 0)))
            out[key] = row
    return out


def binom_two_sided_pvalue(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return math.nan
    k = min(wins, losses)
    p_obs = math.comb(n, k) * (0.5**n)
    p = 0.0
    for i in range(n + 1):
        pi = math.comb(n, i) * (0.5**n)
        if pi <= p_obs + 1e-15:
            p += pi
    return min(1.0, p)


def summarize(
    run_rows: list[dict[str, Any]],
    judged_rows: list[dict[str, Any]],
    models: list[str],
    variants: list[Variant],
) -> dict[str, Any]:
    score_idx: dict[tuple[str, str], list[float]] = defaultdict(list)
    lat_idx: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in judged_rows:
        score_idx[(str(r["model"]), str(r["mode"]))].append(float(r.get("total_score", 0.0)))
    for r in run_rows:
        lat_idx[(str(r["model"]), str(r["mode"]))].append(float(r.get("total_latency_ms", 0.0)))

    out: dict[str, Any] = {"models": {}, "pairwise_vs_direct": {}, "warnings": []}
    for model in models:
        mobj: dict[str, Any] = {"modes": {}}
        direct_s = mean(score_idx[(model, "direct")]) if score_idx[(model, "direct")] else math.nan
        direct_l = mean(lat_idx[(model, "direct")]) if lat_idx[(model, "direct")] else math.nan

        for mode in ["direct"] + [v.name for v in variants]:
            scores = score_idx[(model, mode)]
            lats = lat_idx[(model, mode)]
            mobj["modes"][mode] = {
                "avg_score": mean(scores) if scores else math.nan,
                "avg_latency_ms": mean(lats) if lats else math.nan,
                "rows": len(lats),
                "score_delta_vs_direct": (mean(scores) - direct_s) if scores and not math.isnan(direct_s) else math.nan,
                "latency_delta_vs_direct_ms": (mean(lats) - direct_l) if lats and not math.isnan(direct_l) else math.nan,
            }

            if mode == "direct":
                continue

            direct_by_case: dict[tuple[str, int], float] = {}
            mode_by_case: dict[tuple[str, int], float] = {}
            for row in judged_rows:
                if str(row.get("model")) != model:
                    continue
                key = (str(row.get("prompt_id")), int(row.get("run_index", 0)))
                if str(row.get("mode")) == "direct":
                    direct_by_case[key] = float(row.get("total_score", 0.0))
                elif str(row.get("mode")) == mode:
                    mode_by_case[key] = float(row.get("total_score", 0.0))
            wins = losses = ties = 0
            for key, vscore in mode_by_case.items():
                if key not in direct_by_case:
                    continue
                dscore = direct_by_case[key]
                if vscore > dscore:
                    wins += 1
                elif vscore < dscore:
                    losses += 1
                else:
                    ties += 1
            pval = binom_two_sided_pvalue(wins, losses)
            out["pairwise_vs_direct"][f"{model}:{mode}"] = {
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "non_tie_win_rate": (wins / (wins + losses)) if (wins + losses) else math.nan,
                "pvalue_two_sided_sign_test": pval,
            }

        out["models"][model] = mobj

    return out


def extract_lift_cases(
    judged_rows: list[dict[str, Any]],
    variants: list[Variant],
    min_direct_score: int = 4,
    min_variant_score: int = 6,
) -> list[dict[str, Any]]:
    direct: dict[tuple[str, str, int], float] = {}
    by_key: dict[tuple[str, str, str, int], float] = {}
    for row in judged_rows:
        model = str(row.get("model"))
        prompt_id = str(row.get("prompt_id"))
        run_index = int(row.get("run_index", 0))
        mode = str(row.get("mode"))
        key = (model, prompt_id, run_index)
        if mode == "direct":
            direct[key] = float(row.get("total_score", 0.0))
        else:
            by_key[(model, mode, prompt_id, run_index)] = float(row.get("total_score", 0.0))

    out: list[dict[str, Any]] = []
    for (model, mode, prompt_id, run_index), score in by_key.items():
        d = direct.get((model, prompt_id, run_index))
        if d is None:
            continue
        if d <= min_direct_score and score >= min_variant_score:
            out.append(
                {
                    "model": model,
                    "mode": mode,
                    "prompt_id": prompt_id,
                    "run_index": run_index,
                    "direct_score": d,
                    "variant_score": score,
                    "delta": score - d,
                }
            )
    out.sort(key=lambda r: float(r["delta"]), reverse=True)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run deployment gate for direct vs scaffold variants")
    p.add_argument("--prompt-set", default="docs/evals/prompt_set.jsonl")
    p.add_argument("--out-dir", default="docs/evals/results/variant_gate")
    p.add_argument("--base-dir", default="experiments-local")
    p.add_argument("--variants-file", default="")
    p.add_argument("--top-k-variants", type=int, default=2)
    p.add_argument("--models", nargs="*", default=["qwen2.5:1.5b", "llama3.2:latest"])
    p.add_argument("--runs", type=int, default=2)
    p.add_argument("--ollama-url", default="http://localhost:11434")
    p.add_argument("--request-timeout-s", type=float, default=120.0)
    p.add_argument(
        "--cooldown-every-calls",
        type=int,
        default=0,
        help="Pause after this many model calls (0 disables cooldown).",
    )
    p.add_argument(
        "--cooldown-seconds",
        type=float,
        default=0.0,
        help="Cooldown duration in seconds when --cooldown-every-calls is set.",
    )
    p.add_argument(
        "--strict-direct-groups",
        nargs="*",
        default=[],
        help="Optional prompt groups that should use direct output even for variant modes (task-class lane fallback).",
    )
    p.add_argument("--preset", default="balanced", choices=["fast", "balanced", "strict"])
    p.add_argument("--mode", default="lite", choices=["lite", "two_pass"], help="QuickThink mode used for candidate variants")
    p.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Resume from existing run_results.jsonl in --out-dir. Existing rows are preserved, "
            "missing rows are appended incrementally."
        ),
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    strict_direct_groups = {str(g).strip() for g in args.strict_direct_groups if str(g).strip()}
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt_set = Path(args.prompt_set)
    if not prompt_set.exists():
        raise SystemExit(f"prompt set not found: {prompt_set}")
    prompts = load_prompt_set(prompt_set)
    if not prompts:
        raise SystemExit("prompt set is empty")

    if args.variants_file:
        variants_path = Path(args.variants_file)
    else:
        variants_path = find_latest_pipeline1_variants(Path(args.base_dir))
    variants = load_variants(variants_path, top_k=args.top_k_variants)
    if not variants:
        raise SystemExit("no variants found for evaluation")

    engines_direct: dict[str, QuickThinkEngine] = {}
    engines_variant: dict[tuple[str, str], QuickThinkEngine] = {}
    for model in args.models:
        cfg_direct = QuickThinkConfig.with_model_profile(model=model, ollama_url=args.ollama_url)
        cfg_direct.apply_preset(args.preset)
        cfg_direct.mode = "lite"
        cfg_direct.request_timeout_s = float(args.request_timeout_s)
        cfg_direct.bypass_short_prompts = True
        cfg_direct.adaptive_routing = False
        cfg_direct.bypass_char_threshold = 100_000
        if model_supports_thinking(model):
            cfg_direct.think = False
        engines_direct[model] = QuickThinkEngine(cfg_direct)

        for v in variants:
            cfg_var = QuickThinkConfig.with_model_profile(model=model, ollama_url=args.ollama_url)
            cfg_var.apply_preset(args.preset)
            cfg_var.mode = args.mode
            cfg_var.request_timeout_s = float(args.request_timeout_s)
            cfg_var.scaffold_rules = v.rules
            # Variant gate should measure scaffold behavior, not routing bypass effects.
            cfg_var.bypass_short_prompts = False
            cfg_var.adaptive_routing = False
            if model_supports_thinking(model):
                cfg_var.think = False
            engines_variant[(model, v.name)] = QuickThinkEngine(cfg_var)

    run_path = out_dir / "run_results.jsonl"
    judged_path = out_dir / "judged_results.jsonl"
    summary_json = out_dir / "summary.json"
    summary_md = out_dir / "summary.md"
    lift_path = out_dir / "lift_cases.jsonl"
    meta_path = out_dir / "meta.json"
    checkpoint_path = out_dir / "checkpoint.json"

    existing_keys: set[tuple[str, str, str, int]] = set()
    existing_direct_rows: dict[tuple[str, str, int], dict[str, Any]] = {}
    write_mode = "w"
    if args.resume:
        existing_keys = load_existing_row_keys(run_path)
        existing_direct_rows = load_existing_direct_rows(run_path)
        write_mode = "a"

    total = len(args.models) * len(prompts) * args.runs * (1 + len(variants))
    done = len(existing_keys)
    model_calls = 0

    def maybe_cooldown() -> None:
        nonlocal model_calls
        if args.cooldown_every_calls <= 0 or args.cooldown_seconds <= 0:
            return
        if model_calls > 0 and (model_calls % args.cooldown_every_calls == 0):
            print(
                f"cooldown after {model_calls} model calls: sleeping {args.cooldown_seconds:.0f}s",
                flush=True,
            )
            sleep(float(args.cooldown_seconds))
    if args.resume and existing_keys:
        print(f"resume found {len(existing_keys)} existing rows in {run_path}")

    with run_path.open(write_mode, encoding="utf-8") as out_fh:
        for model in args.models:
            for case in prompts:
                task = str(case["prompt"])
                for run_idx in range(1, args.runs + 1):
                    direct_key = (str(model), "direct", str(case["prompt_id"]), int(run_idx))
                    if direct_key in existing_keys:
                        d = None
                    else:
                        d = engines_direct[model].run(task)
                        model_calls += 1
                        maybe_cooldown()
                        direct_row = {
                            "timestamp": now_iso(),
                            "model": model,
                            "mode": "direct",
                            "prompt_id": case["prompt_id"],
                            "group": case["group"],
                            "run_index": run_idx,
                            "answer": d.answer,
                            "plan": d.plan,
                            "plan_repaired": d.plan_repaired,
                            "bypassed": d.bypassed,
                            "route_score": d.route_score,
                            "selected_plan_budget": d.selected_plan_budget,
                            "plan_latency_ms": float(d.plan_latency_ms),
                            "answer_latency_ms": float(d.answer_latency_ms),
                            "total_latency_ms": float(d.total_latency_ms),
                        }
                        append_jsonl_row(out_fh, direct_row)
                        out_fh.flush()
                        existing_keys.add(direct_key)
                        done += 1
                        if done % 25 == 0 or done == total:
                            checkpoint_path.write_text(
                                json.dumps({"done": done, "total": total, "updated_utc": now_iso()}, indent=2) + "\n",
                                encoding="utf-8",
                            )
                            print(f"progress {done}/{total}")

                    for v in variants:
                        v_key = (str(model), str(v.name), str(case["prompt_id"]), int(run_idx))
                        if v_key in existing_keys:
                            continue
                        if str(case.get("group", "")) in strict_direct_groups:
                            # Task-class lane fallback: strict-format groups use direct output path.
                            if d is None:
                                cached = existing_direct_rows.get((str(model), str(case["prompt_id"]), int(run_idx)))
                                if cached is not None:
                                    v_row = {
                                        "timestamp": now_iso(),
                                        "model": model,
                                        "mode": v.name,
                                        "prompt_id": case["prompt_id"],
                                        "group": case["group"],
                                        "run_index": run_idx,
                                        "answer": str(cached.get("answer", "")),
                                        "plan": cached.get("plan"),
                                        "plan_repaired": bool(cached.get("plan_repaired", False)),
                                        "bypassed": bool(cached.get("bypassed", False)),
                                        "route_score": int(cached.get("route_score", 0)),
                                        "selected_plan_budget": int(cached.get("selected_plan_budget", 0)),
                                        "plan_latency_ms": float(cached.get("plan_latency_ms", 0.0)),
                                        "answer_latency_ms": float(cached.get("answer_latency_ms", 0.0)),
                                        "total_latency_ms": float(cached.get("total_latency_ms", 0.0)),
                                    }
                                    append_jsonl_row(out_fh, v_row)
                                    out_fh.flush()
                                    existing_keys.add(v_key)
                                    done += 1
                                    if done % 25 == 0 or done == total:
                                        checkpoint_path.write_text(
                                            json.dumps({"done": done, "total": total, "updated_utc": now_iso()}, indent=2)
                                            + "\n",
                                            encoding="utf-8",
                                        )
                                        print(f"progress {done}/{total}")
                                    continue
                                d = engines_direct[model].run(task)
                                model_calls += 1
                                maybe_cooldown()
                            r = d
                        else:
                            r = engines_variant[(model, v.name)].run(task)
                            model_calls += 1
                            maybe_cooldown()
                        v_row = {
                            "timestamp": now_iso(),
                            "model": model,
                            "mode": v.name,
                            "prompt_id": case["prompt_id"],
                            "group": case["group"],
                            "run_index": run_idx,
                            "answer": r.answer,
                            "plan": r.plan,
                            "plan_repaired": r.plan_repaired,
                            "bypassed": r.bypassed,
                            "route_score": r.route_score,
                            "selected_plan_budget": r.selected_plan_budget,
                            "plan_latency_ms": float(r.plan_latency_ms),
                            "answer_latency_ms": float(r.answer_latency_ms),
                            "total_latency_ms": float(r.total_latency_ms),
                        }
                        append_jsonl_row(out_fh, v_row)
                        out_fh.flush()
                        existing_keys.add(v_key)
                        done += 1
                        if done % 25 == 0 or done == total:
                            checkpoint_path.write_text(
                                json.dumps({"done": done, "total": total, "updated_utc": now_iso()}, indent=2) + "\n",
                                encoding="utf-8",
                            )
                            print(f"progress {done}/{total}")

    run_rows = load_jsonl_rows(run_path)
    subprocess.run(
        [
            sys.executable,
            "scripts/eval_harness/judge_suite.py",
            "--prompt-set",
            str(prompt_set),
            "--results",
            str(run_path),
            "--out",
            str(judged_path),
            "--backend",
            "rule",
        ],
        check=True,
        text=True,
    )
    judged_rows = [json.loads(l) for l in judged_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    summary = summarize(run_rows, judged_rows, models=args.models, variants=variants)
    lift_cases = extract_lift_cases(judged_rows, variants=variants)

    # Per-group regression warnings vs direct.
    group_scores: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in judged_rows:
        group_scores[(str(row["model"]), str(row["mode"]), str(row["group"]))].append(float(row.get("total_score", 0.0)))
    for model in args.models:
        for v in variants:
            for group in sorted({str(r["group"]) for r in judged_rows if str(r["model"]) == model}):
                dvals = group_scores.get((model, "direct", group), [])
                vvals = group_scores.get((model, v.name, group), [])
                if not dvals or not vvals:
                    continue
                delta = mean(vvals) - mean(dvals)
                if delta <= -0.25:
                    summary["warnings"].append(
                        {
                            "type": "group_regression",
                            "model": model,
                            "mode": v.name,
                            "group": group,
                            "score_delta_vs_direct": delta,
                        }
                    )

    write_jsonl(lift_path, lift_cases)
    summary_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    md: list[str] = [
        "# Variant Deployment Gate",
        "",
        f"- Prompt set: `{prompt_set}`",
        f"- Variants file: `{variants_path}`",
        f"- Variants tested: `{', '.join(v.name for v in variants)}`",
        f"- Models: `{', '.join(args.models)}`",
        f"- Runs per prompt: `{args.runs}`",
        f"- Engine mode for variants: `{args.mode}`",
        f"- Preset: `{args.preset}`",
        f"- Strict-direct groups: `{', '.join(sorted(strict_direct_groups)) if strict_direct_groups else '(none)'}`",
        "",
    ]
    for model in args.models:
        md.append(f"## {model}")
        md.append("")
        md.append("| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |")
        md.append("|---|---:|---:|---:|---:|---:|")
        modes = summary["models"][model]["modes"]
        for mode, vals in sorted(modes.items()):
            md.append(
                f"| {mode} | {vals['avg_score']:.3f} | {vals['score_delta_vs_direct']:.3f} | "
                f"{vals['avg_latency_ms']:.2f} | {vals['latency_delta_vs_direct_ms']:.2f} | {vals['rows']} |"
            )
        md.append("")
        md.append("### Pairwise vs direct")
        md.append("")
        md.append("| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |")
        md.append("|---|---:|---:|---:|---:|---:|")
        for v in variants:
            key = f"{model}:{v.name}"
            p = summary["pairwise_vs_direct"].get(key, {})
            md.append(
                f"| {v.name} | {int(p.get('wins', 0))} | {int(p.get('losses', 0))} | {int(p.get('ties', 0))} | "
                f"{float(p.get('non_tie_win_rate', math.nan)):.3f} | {float(p.get('pvalue_two_sided_sign_test', math.nan)):.4f} |"
            )
        md.append("")

    md.extend(["## Lift Cases", "", "Cases where direct<=4 and variant>=6 in same prompt/run.", ""])
    for row in lift_cases[:50]:
        md.append(
            f"- {row['model']} {row['mode']} {row['prompt_id']}#run{row['run_index']}: "
            f"direct={row['direct_score']:.1f} variant={row['variant_score']:.1f} delta={row['delta']:.1f}"
        )
    if summary.get("warnings"):
        md.extend(["", "## Warnings", ""])
        for w in summary["warnings"]:
            md.append(
                f"- {w['type']}: model={w['model']} mode={w['mode']} group={w['group']} "
                f"score_delta_vs_direct={w['score_delta_vs_direct']:.3f}"
            )
    summary_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    meta = {
        "created_utc": now_iso(),
        "prompt_set": str(prompt_set),
        "variants_file": str(variants_path),
        "variants_tested": [v.name for v in variants],
        "models": args.models,
        "runs": args.runs,
        "resume": bool(args.resume),
        "strict_direct_groups": sorted(strict_direct_groups),
        "rows": len(run_rows),
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"status=OK out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
