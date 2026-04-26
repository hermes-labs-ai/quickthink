#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

TASK_CLASS_BY_GROUP = {
    "instruction_constraints": "strict_format",
    "structured_output": "strict_format",
    "reasoning": "reasoning",
    "multi_turn_continuity": "continuity",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def model_family(model: str) -> str:
    m = re.match(r"([a-zA-Z]+)", model)
    if m:
        return m.group(1).lower()
    return model.split(":")[0].lower()


def task_class(group: str) -> str:
    return TASK_CLASS_BY_GROUP.get(group, "other")


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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build PASS/FAIL/INCONCLUSIVE lane decisions from eval artifacts")
    p.add_argument("--runs-jsonl", required=True, help="Run rows JSONL path")
    p.add_argument("--judged-jsonl", required=True, help="Judged rows JSONL path")
    p.add_argument("--out", required=True, help="Output decision JSON")
    p.add_argument("--run-id", default="", help="Optional run id label")
    p.add_argument("--threshold-profile", default="deployment_gate_2026")
    p.add_argument("--non-tie-win-rate-min", type=float, default=0.55)
    p.add_argument("--pvalue-max", type=float, default=0.10)
    p.add_argument("--latency-delta-max-ms", type=float, default=-50.0)
    p.add_argument("--lift-cases-min", type=int, default=5)
    p.add_argument("--regression-threshold", type=float, default=-0.25)
    p.add_argument("--min-pairs", type=int, default=12, help="Minimum paired non-missing comparisons per lane")
    p.add_argument(
        "--backend-stable",
        action="store_true",
        help="Mark this run as backend-stable. If not set, all lanes are INCONCLUSIVE.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    run_rows = load_jsonl(Path(args.runs_jsonl))
    judged_rows = load_jsonl(Path(args.judged_jsonl))
    if not run_rows:
        raise SystemExit("no run rows found")
    if not judged_rows:
        raise SystemExit("no judged rows found")

    # Build latency index and score index by (model, mode, task_class, prompt_id, run_index).
    lat_by_key: dict[tuple[str, str, str, str, int], float] = {}
    for r in run_rows:
        model = str(r.get("model", ""))
        mode = str(r.get("mode", ""))
        group = str(r.get("group", ""))
        tclass = task_class(group)
        prompt_id = str(r.get("prompt_id", ""))
        run_index = int(r.get("run_index", 0))
        key = (model, mode, tclass, prompt_id, run_index)
        lat_by_key[key] = float(r.get("total_latency_ms", 0.0))

    score_by_key: dict[tuple[str, str, str, str, int], float] = {}
    group_by_key: dict[tuple[str, str, str, str, int], str] = {}
    models: set[str] = set()
    modes: set[str] = set()
    for r in judged_rows:
        model = str(r.get("model", ""))
        mode = str(r.get("mode", ""))
        group = str(r.get("group", ""))
        tclass = task_class(group)
        prompt_id = str(r.get("prompt_id", ""))
        run_index = int(r.get("run_index", 0))
        key = (model, mode, tclass, prompt_id, run_index)
        score_by_key[key] = float(r.get("total_score", 0.0))
        group_by_key[key] = group
        models.add(model)
        modes.add(mode)

    if "direct" not in modes:
        raise SystemExit("direct mode not found in judged rows")

    lane_rows: list[dict[str, Any]] = []
    task_classes = sorted({task_class(str(r.get("group", ""))) for r in judged_rows})
    for model in sorted(models):
        fam = model_family(model)
        for mode in sorted(m for m in modes if m != "direct"):
            for tclass in task_classes:
                direct_scores: dict[tuple[str, int], float] = {}
                mode_scores: dict[tuple[str, int], float] = {}
                direct_lats: list[float] = []
                mode_lats: list[float] = []
                per_group_direct: dict[str, list[float]] = defaultdict(list)
                per_group_mode: dict[str, list[float]] = defaultdict(list)

                for key, s in score_by_key.items():
                    km, kmode, ktclass, prompt_id, run_index = key
                    if km != model or ktclass != tclass:
                        continue
                    grp = group_by_key[key]
                    if kmode == "direct":
                        direct_scores[(prompt_id, run_index)] = s
                        per_group_direct[grp].append(s)
                    elif kmode == mode:
                        mode_scores[(prompt_id, run_index)] = s
                        per_group_mode[grp].append(s)

                # Paired comparisons.
                wins = losses = ties = 0
                paired_d_scores: list[float] = []
                paired_m_scores: list[float] = []
                for case_key, ms in mode_scores.items():
                    ds = direct_scores.get(case_key)
                    if ds is None:
                        continue
                    paired_m_scores.append(ms)
                    paired_d_scores.append(ds)
                    if ms > ds:
                        wins += 1
                    elif ms < ds:
                        losses += 1
                    else:
                        ties += 1

                    prompt_id, run_index = case_key
                    dlat = lat_by_key.get((model, "direct", tclass, prompt_id, run_index))
                    mlat = lat_by_key.get((model, mode, tclass, prompt_id, run_index))
                    if dlat is not None and mlat is not None:
                        direct_lats.append(dlat)
                        mode_lats.append(mlat)

                pair_count = wins + losses + ties
                non_ties = wins + losses
                non_tie_win_rate = (wins / non_ties) if non_ties else math.nan
                pvalue = binom_two_sided_pvalue(wins, losses)
                score_delta = (mean(paired_m_scores) - mean(paired_d_scores)) if paired_d_scores else math.nan
                latency_delta_ms = (mean(mode_lats) - mean(direct_lats)) if direct_lats and mode_lats else math.nan

                # Lift cases: direct<=4 and mode>=6.
                lift_cases = 0
                for case_key, ms in mode_scores.items():
                    ds = direct_scores.get(case_key)
                    if ds is None:
                        continue
                    if ds <= 4.0 and ms >= 6.0:
                        lift_cases += 1

                # Per-group regressions for this lane.
                regressions: list[dict[str, Any]] = []
                for grp in sorted(set(per_group_direct.keys()) | set(per_group_mode.keys())):
                    dvals = per_group_direct.get(grp, [])
                    mvals = per_group_mode.get(grp, [])
                    if not dvals or not mvals:
                        continue
                    delta = mean(mvals) - mean(dvals)
                    if delta <= args.regression_threshold:
                        regressions.append({"group": grp, "score_delta_vs_direct": delta})

                reasons: list[str] = []
                decision = "PASS"
                if not args.backend_stable:
                    decision = "INCONCLUSIVE"
                    reasons.append("backend_marked_unstable")
                if pair_count < args.min_pairs:
                    decision = "INCONCLUSIVE"
                    reasons.append(f"insufficient_pairs<{args.min_pairs}")
                if non_ties == 0:
                    decision = "INCONCLUSIVE"
                    reasons.append("no_non_tie_pairs")

                if decision != "INCONCLUSIVE":
                    if math.isnan(non_tie_win_rate) or non_tie_win_rate < args.non_tie_win_rate_min:
                        decision = "FAIL"
                        reasons.append("win_rate_below_threshold")
                    if math.isnan(pvalue) or pvalue > args.pvalue_max:
                        decision = "FAIL"
                        reasons.append("pvalue_above_threshold")
                    if math.isnan(latency_delta_ms) or latency_delta_ms > args.latency_delta_max_ms:
                        decision = "FAIL"
                        reasons.append("latency_delta_not_good_enough")
                    if lift_cases < args.lift_cases_min:
                        decision = "FAIL"
                        reasons.append("insufficient_lift_cases")
                    if regressions:
                        decision = "FAIL"
                        reasons.append("group_regression_detected")
                    if not reasons:
                        reasons.append("all_thresholds_met")

                lane_rows.append(
                    {
                        "task_class": tclass,
                        "model": model,
                        "model_family": fam,
                        "mode": mode,
                        "decision": decision,
                        "metrics": {
                            "wins": wins,
                            "losses": losses,
                            "ties": ties,
                            "pair_count": pair_count,
                            "non_tie_win_rate": non_tie_win_rate,
                            "sign_test_pvalue": pvalue,
                            "score_delta_vs_direct": score_delta,
                            "latency_delta_ms_vs_direct": latency_delta_ms,
                            "lift_cases": lift_cases,
                            "group_regressions": regressions,
                        },
                        "sample_size_rows": pair_count,
                        "decision_reason": ";".join(reasons),
                    }
                )

    out = {
        "run_id": args.run_id or Path(args.runs_jsonl).parent.name,
        "threshold_profile": args.threshold_profile,
        "config": {
            "non_tie_win_rate_min": args.non_tie_win_rate_min,
            "pvalue_max": args.pvalue_max,
            "latency_delta_max_ms": args.latency_delta_max_ms,
            "lift_cases_min": args.lift_cases_min,
            "regression_threshold": args.regression_threshold,
            "min_pairs": args.min_pairs,
            "backend_stable": bool(args.backend_stable),
        },
        "lanes": sorted(lane_rows, key=lambda r: (r["task_class"], r["model"], r["mode"])),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote gate decision: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
