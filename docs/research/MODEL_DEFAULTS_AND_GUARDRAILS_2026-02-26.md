# Model Defaults And Guardrails

## Purpose
Define operational default scaffold choices per model, with explicit lane guardrails and confidence labels based on current evidence.

## Inputs
- `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n8_full/summary.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n5_full/summary.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/run_llama31_8b_n5_top3/summary.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/run_gemma2_9b_n5_top3/summary.md`

## Defaults (current)
1. `qwen2.5:1.5b`:
- Default scaffold: `v02_language_game_moves`
- Confidence: `high`
- Guardrails: none required for current default lane set

2. `mistral:7b`:
- Default scaffold: `v01_anchor_dual_relation`
- Alternate strong option: `v11_repair_then_realize` (if lane constraints permit)
- Confidence: `high`
- Guardrails: apply lane checks per `DECISION_GATES.md`

3. `llama3.1:8b`:
- Default scaffold: `v02_language_game_moves`
- Confidence: `medium-high`
- Guardrails (current): fallback to `direct` for `multi_turn_continuity` and `instruction_constraints`
- Evidence note: guarded validation run improved delta to `+0.267` with stronger pairwise win rate, but instruction regression warning remained.

4. `gemma2:9b`:
- Default scaffold: `v01_anchor_dual_relation`
- Confidence: `low-medium`
- Guardrails (current): fallback to `direct` for `reasoning`
- Evidence note: guarded reasoning fallback run improved delta to `+0.150` and cleared warnings, but pairwise strength remained weak (`0.500`).

## Why these defaults
- Defaults were selected by a combination of positive global delta, warning profile, and comparative cross-model stability.
- Confidence is reduced when pairwise win strength is weak or lane regressions are persistent.

## Operational policy
- Model-specific defaults are required.
- No universal scaffold default across all models.
- When a blocked lane is detected, route to `direct`.

## Outputs
- Human-readable policy: this file
- Machine-readable policy: `experiments-local/operations/model_routing_policy_v1.json`

## Limits
- This is a snapshot policy and must be revised as new runs are added.
