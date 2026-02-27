# Phenomenology Significance Report - 2026-02-25

## Status
Completed experiment report for cross-agent handoff.

## Purpose
Summarize significance-focused follow-up experiments on conceptually motivated scaffold variants for QuickThink and identify candidates with statistically meaningful lift vs direct mode.

## Inputs
- Baseline broad concept run:
  - `/Users/rolibosch/Documents/QuickThink/docs/research/codex/experiments/phenomenology_run_2026-02-25_n5_full_01/summary.json`
- Follow-up significance run (top 3 variants):
  - `/Users/rolibosch/Documents/QuickThink/docs/research/codex/experiments/phenomenology_run_2026-02-25_top3_n15/summary.json`
- Artifacts:
  - `/Users/rolibosch/Documents/QuickThink/docs/research/codex/experiments/phenomenology_run_2026-02-25_top3_n15/run_results.jsonl`
  - `/Users/rolibosch/Documents/QuickThink/docs/research/codex/experiments/phenomenology_run_2026-02-25_top3_n15/judged_results.jsonl`
  - `/Users/rolibosch/Documents/QuickThink/docs/research/codex/experiments/phenomenology_run_2026-02-25_top3_n15/lift_cases.jsonl`

## Method
- Canonical runner: `scripts/eval_harness/run_variant_gate.py`
- Model: `qwen2.5:1.5b`
- Prompt subset: 12 balanced prompts (`instruction_constraints`, `multi_turn_continuity`, `reasoning`, `structured_output`)
- Evaluation: paired vs `direct` with sign-test p-values on non-tie outcomes.

## N Design
Run A (screening):
- Variants: 12
- Runs per prompt: 5
- Paired observations per variant vs direct: up to `N=60`

Run B (significance-focused):
- Variants: 3 (`v02`, `v03`, `v04`)
- Runs per prompt: 15
- Paired observations per variant vs direct: up to `N=180`

## Results
### Run A (12 variants, N up to 60 each)
- Directional leaders by average score delta:
  1. `v04_negative_capability` (`+0.15`)
  2. `v03_horizon_fusion_guard` (`+0.1167`)
  3. `v02_language_game_moves` (`+0.0833`)
- Significance status:
  - No variant reached two-sided `p < 0.05`.
- Interpretation:
  - Useful screening signal only.

### Run B (top 3 variants, N up to 180 each)
Direct baseline:
- avg score: `5.5444`
- avg latency: `2199.68 ms`
- rows: `180`

Variant outcomes:
1. `v02_language_game_moves`
- avg score: `5.8389`
- score delta vs direct: `+0.2944`
- wins/losses/ties: `45 / 21 / 114`
- non-tie win rate: `0.6818`
- two-sided sign-test p-value: `0.00427` (statistically significant)
- avg latency delta: `-582.23 ms`

2. `v03_horizon_fusion_guard`
- avg score: `5.7778`
- score delta vs direct: `+0.2333`
- wins/losses/ties: `39 / 22 / 119`
- non-tie win rate: `0.6393`
- two-sided sign-test p-value: `0.03962` (statistically significant)
- avg latency delta: `-719.07 ms`

3. `v04_negative_capability`
- avg score: `5.7000`
- score delta vs direct: `+0.1556`
- wins/losses/ties: `44 / 29 / 107`
- non-tie win rate: `0.6027`
- two-sided sign-test p-value: `0.10064` (not significant at 0.05)
- avg latency delta: `-482.84 ms`

Lift cases:
- `31` lift cases recorded in run B.
- Several strong lifts are concentrated in reasoning prompts (notably `R002`).

Regression warnings:
- 1 warning in run B:
  - `v04_negative_capability` regressed on `structured_output` group (`-0.4667`).

## Interpretation
1. Statistical significance was achieved for two concept variants after increasing N.
2. `v02` is currently the strongest candidate by both effect size and p-value.
3. `v03` is a second viable candidate with significant but smaller effect.
4. `v04` remains directionally positive overall but insufficiently consistent for significance and shows structured-output risk.

## Recommendations
Must:
1. Advance `v02_language_game_moves` and `v03_horizon_fusion_guard` to cross-model confirmation (`mistral:7b`).
2. Keep `v04` as a conditional/ablation candidate, not primary rollout candidate.
3. Preserve per-group gating checks to prevent silent regressions in structured-output tasks.

May:
1. Build a hybrid lane where strict structured-output tasks bypass philosophical scaffolds.
2. Run ablations that isolate which tokens/rules in `v02` and `v03` drive lift.

## Commands
Run B command used:

```bash
PYTHONPATH=src python3 -u scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl \
  --out-dir docs/research/codex/experiments/phenomenology_run_2026-02-25_top3_n15 \
  --variants-file docs/research/codex/experiments/phenomenology_variants_top3_2026-02-25.json \
  --top-k-variants 3 \
  --models qwen2.5:1.5b \
  --runs 15 \
  --preset balanced \
  --mode lite
```

## Limits
1. Judge backend is rule-based; findings should be treated as strong internal evidence, not final external proof.
2. Prompt subset is balanced but limited (12 prompts).
3. Results are currently demonstrated on one model lane.
4. High tie counts mean pairwise sensitivity is bounded; p-values are still informative but conservative.
