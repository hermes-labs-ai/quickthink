# R&D Ledger

## Purpose
Maintain a single, date-ordered log of research direction, decisions, and evidence quality so progress is auditable across agents and sessions.

## Usage Rules
1. Append only (do not rewrite historical entries except for factual corrections).
2. One entry per meaningful research session or experiment wave.
3. Every entry must reference concrete artifact paths.
4. Distinguish `Observed` from `Interpreted` claims.

## Entry Template
### Entry <UTC timestamp>
- Owner:
- Session framing:
- Objective tier (`no-loss-first` | `balanced` | `max-gain`):
- Inputs:
- Runs added:
- Observed:
- Interpreted:
- Decision impact:
- Next experiments:

## Latest Entries
### Entry 2026-02-26T17:59:30Z
- Owner: Codex
- Session framing: decision-ready synthesis after expanded runs
- Objective tier: pending user selection (`no-loss-first` vs `balanced`)
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n8_full/summary.json`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n5_full/summary.json`
- Runs added:
  - `run_qwen_n8_full`
  - `run_mistral_n5_full`
- Observed:
  - Cross-model positive set exists (`v01`, `v02`, `v08`) with stronger mistral lift.
  - Qwen structured-output regressions persist in many variants.
- Interpreted:
  - Lane-specific policy remains more defensible than one global winner.
- Decision impact:
  - Candidate short list should prioritize `v02`, `v01`, with guarded use of `v08`.
- Next experiments:
  - Weak-model litmus test on short list under selected objective tier.

### Entry 2026-02-26T18:20:00Z
- Owner: Codex
- Session framing: market-depth decision memo for GTM tier selection
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): recommendation = `balanced` default + `no-loss-first` package option
- Inputs:
  - `docs/research/GTM_TIER_DECISION_MEMO_2026-02-26.md`
  - `docs/research/DECISION_GATES.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n8_full/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n5_full/summary.md`
- Runs added:
  - none (synthesis session)
- Observed:
  - External market signals indicate ROI + trust/governance discipline in enterprise buying.
  - Internal evidence shows uplift with lane-specific regression risk.
- Interpreted:
  - `balanced` is the most scalable default posture; `no-loss-first` should be a stricter option.
- Decision impact:
  - GTM baseline can now be set without waiting for perfect no-regression across all lanes.
- Next experiments:
  - Weak-model litmus tests on short-listed variants under `balanced` gate.

### Entry 2026-02-26T19:05:00Z
- Owner: Codex
- Session framing: 4-model expansion pass (llama/gemma additions) on top-3 shortlist
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): evaluated under `balanced` lens (decision pending)
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_llama31_8b_n5_top3/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_gemma2_9b_n5_top3/summary.md`
  - existing anchors: `run_qwen_n8_full`, `run_mistral_n5_full`
- Runs added:
  - `run_llama31_8b_n5_top3`
  - `run_gemma2_9b_n5_top3`
- Observed:
  - `llama3.1:8b`: mild positive deltas for all 3 variants (`v02` strongest), but weak pairwise signal and subgroup warnings.
  - `gemma2:9b`: only `v01` positive; `v02` and `v08` negative vs direct; reasoning regressions flagged.
  - Latency improved for all variants on both new models.
- Interpreted:
  - Cross-model transfer exists but is heterogeneous; shortlist does not yet deliver robust win consistency across all four models.
  - Current evidence supports guarded/lane-specific deployment logic over a single universal scaffold policy.
- Decision impact:
  - 4-model gate raises confidence in `v01` robustness relative to `v02`/`v08`, but not enough for broad no-guardrail promotion.
- Next experiments:
  - Run `qwen2.5:14b` replacement for the small qwen slot and compare with `qwen2.5:1.5b` drift.
  - Consider variant tweaks for reasoning-lane preservation on gemma/llama.

### Entry 2026-02-26T19:25:00Z
- Owner: Codex
- Session framing: targeted llama confidence-upgrade validation (`v02` guarded)
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_llama31_8b_n5_v02_guarded/summary.md`
  - `experiments-local/operations/model_routing_policy_v1.json`
- Runs added:
  - `run_llama31_8b_n5_v02_guarded`
- Observed:
  - `v02` improved to `+0.267` with `non_tie_win_rate=0.619` and strong latency reduction.
  - Remaining warning: `instruction_constraints` regression (`-0.333`).
- Interpreted:
  - Llama confidence improved from medium to medium-high, contingent on stricter lane guardrails.
- Decision impact:
  - Llama can be used with `v02` default under explicit lane fallback (`multi_turn_continuity`, `instruction_constraints`).
- Next experiments:
  - Apply analogous guarded run for gemma (`v01` + reasoning fallback) to raise gemma confidence.

### Entry 2026-02-26T19:45:00Z
- Owner: Codex
- Session framing: targeted gemma confidence-upgrade validation (`v01` guarded)
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_gemma2_9b_n5_v01_guarded/summary.md`
  - `experiments-local/operations/CONFIDENCE_UPGRADE_PLAN_V1.md`
- Runs added:
  - `run_gemma2_9b_n5_v01_guarded`
- Observed:
  - `v01` improved to `+0.150` and reasoning warnings cleared under strict-direct reasoning fallback.
  - Pairwise consistency remained weak (`non_tie_win_rate=0.500`).
- Interpreted:
  - Gemma upgrade is partial: safer and modestly better, but not yet strong enough for high-confidence default claim.
- Decision impact:
  - Keep gemma confidence at `low-medium`; retain reasoning fallback guardrail.
- Next experiments:
  - Increase gemma run count and/or test a refined variant to improve pairwise consistency.

### Entry 2026-02-26T20:05:00Z
- Owner: Codex
- Session framing: parallel local+API benchmark execution
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced` (evaluation only)
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen25_14b_n5_top3/summary.md`
  - `/Users/rolibosch/Documents/Claude Code/haiku45-baseline-2026-02-26.json`
- Runs added:
  - `run_qwen25_14b_n5_top3`
  - `anthropic_baseline/haiku45_no_canary_2026-02-26`
- Observed:
  - `qwen2.5:14b`: `v01` slightly positive (`+0.083`), while `v02` and `v08` regressed globally; structured-output regressions flagged for `v02/v08`.
  - Haiku 4.5 baseline benchmark returned `100% refused` on this adversarial benchmark set.
- Interpreted:
  - Larger qwen tier changes shortlist behavior materially (weakens prior `v02` optimism).
  - API baseline datapoint is useful but needs harness alignment before direct comparison against local variant-gate results.
- Decision impact:
  - Prefer `v01` over `v02/v08` for qwen14 provisional default testing.
- Next experiments:
  - Add guarded qwen14 `v01` run for lane-risk reduction.
  - Build aligned API variant-gate harness for apples-to-apples comparison.

### Entry 2026-02-26T23:47:00Z
- Owner: Codex
- Session framing: first QuickThink-aligned API run (Haiku) to replace canary-only baseline
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_haiku45_n5_top3/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/phenomenology_variants_top3_focus.json`
  - `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- Runs added:
  - `run_haiku45_n5_top3`
- Observed:
  - All three variants slightly negative vs direct (`v01 -0.067`, `v02 -0.067`, `v08 -0.017`) with weak pairwise lift (non-tie win rates 0.30/0.25/0.44; p>0.28).
  - Instruction_constraints regressions flagged for all variants (`-0.333`); latency roughly on par with direct (v02 slightly faster).
- Interpreted:
  - QuickThink scaffolds do not improve Anthropic Haiku on the balanced12 set; direct remains the safest default.
  - API client wiring is validated; future gains require variant retuning or lane-specific guardrails for instruction-constrained tasks.
- Decision impact:
  - Keep Haiku in direct/default lane; do not promote scaffold variants for Haiku until new evidence shows lift.
- Next experiments:
  - Try guardrail-first or trimmed variants tailored to instruction_constraints for Haiku, or swap in alternative Anthropic model if available.

### Entry 2026-02-27T00:15:00Z
- Owner: Codex
- Session framing: Haiku quick-turn mini-experiments to diagnose instruction regressions
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_haiku45_guardrails_n2/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_haiku45_trimmed_n2/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_haiku45_instrfirst_n2/summary.md`
- Runs added:
  - `run_haiku45_guardrails_n2`
  - `run_haiku45_trimmed_n2`
  - `run_haiku45_instrfirst_n2`
- Observed:
  - Guardrail-only (v01 + strict-direct instruction_constraints): delta -0.083, win_rate 0.0, structured_output regression.
  - Trimmed scaffold (v02_trimmed): delta -0.042, win_rate 0.33, instruction_constraints regression persists; latency -250 ms.
  - Instruction-first preamble (v03): delta -0.125, win_rate 0.25, instruction_constraints regression -0.5; fastest latency (-330 ms).
- Interpreted:
  - Instruction lane remains the failure point across tweaks; simple guardrails/preambles are insufficient.
  - Latency can be improved with shorter scaffolds, but accuracy trade-off is unacceptable for promotion.
- Decision impact:
  - Keep Haiku on direct-only; next iteration should target instruction_constraints-specific prompting or alternative Anthropic model.
- Next experiments:
  - Design instruction-lane-specific scaffold for Haiku (e.g., explicit JSON validator step) and retest with small n.
  - Consider Sonnet/Opus check if API budget allows to see if higher tiers respond better to scaffolding.

### Entry 2026-02-27T00:40:00Z
- Owner: Codex
- Session framing: instruction-lane prototypes across Haiku and local qwen
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_haiku45_instrlane_n4/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen15_instrlane_n4/summary.md`
- Runs added:
  - `run_haiku45_instrlane_n4`
  - `run_qwen15_instrlane_n4`
- Observed:
  - Haiku: instruction-focused variants remain negative vs direct (v10 -0.188, v11 -0.083) with instruction/structured_output regressions; small latency gains.
  - qwen1.5b: both variants lift scores (v10 +0.292, v11 +0.271) and cut latency (~-0.9 to -1.1s); v11 avoids structured_output regression, v10 flagged.
- Interpreted:
  - The scaffold is effective for qwen in instruction lane but not for Haiku; model-specific tuning needed.
  - v11 looks like the safer instruction-default candidate on qwen; Haiku still requires direct or different scaffold.
- Decision impact:
  - Keep Haiku direct-only; consider adopting v11 as instruction-lane default for qwen after larger-n confirmation.
- Next experiments:
  - Finish mistral instruction-lane run (in progress/stalled) or re-run with a reliable harness.
  - Try a Haiku-specific instruction fixer (e.g., explicit JSON echo + retry) or escalate to Sonnet/Opus if budgeted.

### Entry 2026-02-27T01:35:00Z
- Owner: Codex
- Session framing: Haiku JSON-echo attempt; qwen v11 long-run started
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_haiku45_json_echo_n4/summary.md`
  - (partial) `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen15_v11_instr_n8/run_results.jsonl`
- Runs added:
  - `run_haiku45_json_echo_n4`
  - `run_qwen15_v11_instr_n8` (incomplete; stopped at 122/192 rows, no summary yet)
- Observed:
  - Haiku JSON-echo variants: v12 -0.042, v13 -0.125 vs direct; instruction_constraints regressions remain; small latency gains.
  - qwen v11 n=8 run stalled partway; data insufficient for summary yet.
- Interpreted:
  - JSON echo/validator did not fix Haiku instruction regressions; Haiku stays direct-only.
  - Need to rerun qwen v11 confirmation to completion; partial data still consistent with earlier positive direction.
- Decision impact:
  - No change to defaults until qwen confirmation completes; Haiku remains direct lane.
- Next experiments:
  - Restart qwen v11 confirmation (consider reduced prompt subset to ensure completion).
  - If time remains, retry mistral instruction lane with reduced prompt subset.

### Entry 2026-02-27T09:00:28Z
- Owner: Codex
- Session framing: thread-loss recovery and canonical state reconstruction for multi-agent orchestration
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced` (planning/synthesis)
- Inputs:
  - `AGENTS.md`
  - `FOLDER_MAP.md`
  - `docs/AGENT_BOOTSTRAP.md`
  - `docs/MARKDOWN_INDEX.md`
  - `docs/research/DECISION_GATES.md`
  - `docs/research/MODEL_DEFAULTS_AND_GUARDRAILS_2026-02-26.md`
  - `docs/research/instruction_lane_iterative_loop_2026-02-27.md`
  - `experiments-local/registry/INDEX.md`
  - `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md`
- Runs added:
  - `research_orchestration/session_recovery_2026-02-27` (reference synthesis trace)
- Observed:
  - Canonical research memory is recoverable from ledger/registry/policy docs without relying on chat history.
  - Current unresolved queue is instruction-lane confirmation work (`qwen v11` completion, mistral rerun) with Haiku still failing scaffold gates.
  - Documentation closeout protocol and hygiene checks are available and enforceable in-repo.
- Interpreted:
  - The project can operate safely with multi-assistant orchestration if strict writeback rules are enforced (ledger + registry + indexed docs).
  - Rules are most reliable when objective and file-checkable, not prose-only guidance.
- Decision impact:
  - Established `docs/research/THREAD_RECOVERY_MAP_2026-02-27.md` as restart anchor for this phase.
  - Preserved continuity with explicit registry trace and index updates to reduce future context-loss risk.
- Next experiments:
  - Complete qwen instruction-lane confirmation at larger N with fresh run directory.
  - Re-run mistral instruction-lane variants under stable execution settings.
  - Decide whether to continue Haiku lane exploration or pause in favor of higher-tier Anthropic test.

### Entry 2026-02-27T12:12:12Z
- Owner: Codex
- Session framing: throttled continuation run under machine-safety cooldown policy
- Objective tier (`no-loss-first` | `balanced` | `max-gain`): `balanced`
- Inputs:
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen15_v11_instr_n8_rerun_2026-02-27/summary.md`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen15_v11_instr_n8_rerun_2026-02-27/summary.json`
  - `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_instrlane_n1_rerun_2026-02-27/run_results.jsonl` (partial)
- Runs added:
  - `run_qwen15_v11_instr_n8_rerun_2026-02-27`
- Observed:
  - qwen1.5b `v11_instruction_validator` at n=8 is slightly negative vs direct (`score_delta_vs_direct=-0.031`) with weak pairwise signal (`wins=21 losses=22 ties=53`).
  - `structured_output` regressed for qwen v11 (`score_delta_vs_direct=-0.542`); latency was slightly worse (`+8.44ms`).
  - mistral throttled rerun was started but intentionally stopped early at 11/36 rows due conservative cooldown pacing and time budget.
- Interpreted:
  - Earlier small-n qwen optimism for v11 does not hold at larger sample size.
  - qwen instruction-lane default should remain `direct` unless a revised variant clears structured-output gates.
  - 5-minute cooldown every 6 model calls is operationally safe but materially slows throughput; planning must account for this.
- Decision impact:
  - qwen instruction-lane recommendation shifts from candidate-promote to `HOLD` under `balanced` gates.
  - mistral instruction-lane remains unresolved pending completed run.
- Next experiments:
  - Design/refine qwen instruction variant that explicitly protects structured_output and rerun at n>=4 before reconsidering promotion.
  - Resume mistral run with the same cooldown policy to full completion (or reduce prompt subset with documented scope).
