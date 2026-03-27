# Decision Gates

## Purpose
Define fixed decision thresholds for experiment interpretation so agents make comparable rollout recommendations across sessions.

## Inputs
- Per-run `summary.json` / `summary.md`
- Per-run warnings (`group_regression` entries)
- Cross-model comparisons for the same variant set

## Objective tiers

### 1. No-Loss-First
Use when reliability and regression avoidance dominate.

Promotion criteria (must satisfy all):
1. `score_delta_vs_direct >= 0.00` on each required model.
2. No `group_regression` warnings in required lanes.
3. `non_tie_win_rate >= 0.55` where non-tie pairs exist.
4. No severe subgroup delta worse than `-0.25`.

### 2. Balanced (default)
Use when risk-adjusted uplift is the goal.

Promotion criteria (must satisfy all):
1. `score_delta_vs_direct >= +0.10` on primary model and `>= 0.00` on secondary model(s).
2. At most 1 warning lane, and no severe subgroup delta worse than `-0.50`.
3. `non_tie_win_rate >= 0.60` on primary model.
4. If any lane regresses, global uplift must be at least `+0.25` on primary model.

### 3. Max-Gain
Use when exploration and peak uplift dominate.

Promotion criteria (must satisfy all):
1. `score_delta_vs_direct >= +0.25` on target model.
2. Regressions are allowed but must be explicitly listed in recommendation.
3. `non_tie_win_rate >= 0.60` or sign-test p-value indicates directional support.
4. Mark recommendation as `model-bound` unless cross-model evidence is positive.

## Required output labels
All recommendations must include one of:
- `PROMOTE`
- `PROMOTE_WITH_GUARDRAILS`
- `HOLD`
- `REJECT`

And must include:
- Objective tier used
- Models considered
- Required lane constraints
- Evidence paths

## Commands
Use canonical harness artifacts; no special command is required for this gate file.

## Limits
1. Thresholds are operational defaults; they can be revised with explicit note in `R_AND_D_LEDGER.md`.
2. This gate assumes judged results are valid; fallback-only judge outputs are non-decision-grade.
