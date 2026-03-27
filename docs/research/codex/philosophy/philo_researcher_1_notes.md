# Philo Researcher #1 Notes

## Status
Exploratory working notes for experiment design and interpretation.

## Purpose
Record the conceptual framing, assumptions, hypotheses, and interpretation rules used when running philosophical/hermeneutic scaffold experiments in QuickThink.

## Scope
These notes are for research traceability only.
- They must not be treated as product claims.
- They may guide experiment design, not runtime behavior changes by default.

## Framing
1. Representation is intervention:
- Prompt/scaffold structure is treated as a control surface, not a neutral wrapper.
2. Language-games framing:
- Variants are tested as rule-governed move sets, not style tweaks.
3. Hermeneutic framing:
- Variants are treated as pre-structures that can narrow or bias interpretation horizons.
4. Anchor principle:
- Better outcomes are expected when there is explicit relation between task constraints and generated answer behavior.

## Assumptions
1. Small structural prompt changes can produce measurable downstream behavior differences.
2. Effects are task-class dependent (reasoning vs structured-output vs constraints vs continuity).
3. Average score improvements may hide subgroup regressions; group-level checks are required.
4. Rule-based judging is useful for screening, but insufficient for final claims.
5. Single-model wins are not cross-model wins.
6. Local lift cases matter, but isolated wins are not enough for rollout.

## Hypotheses
1. H1: Relation-anchored variants improve average score over direct baseline on mixed subsets.
2. H2: Some variants produce concentrated gains on reasoning tasks while regressing structured-output tasks.
3. H3: Constraint-priority variants reduce format failures but may reduce semantic richness.
4. H4: Negative-capability style variants reduce overclaiming and improve robustness under ambiguity.
5. H5: No single variant dominates across all groups; lane-specific routing is likely superior.

## Experiment Posture
1. Must run paired comparisons vs direct baseline.
2. Must report both global deltas and per-group deltas.
3. Must track wins/losses/ties and sign-test p-values for non-tie pairs.
4. Must log lift cases and regression warnings.
5. Must avoid universal language ("always", "guaranteed", "solved").

## Interpretation Rules
1. Promote only variants that satisfy all:
- positive or neutral global delta,
- no severe repeated group regressions,
- acceptable latency tradeoff,
- reproducibility in at least one additional lane.
2. Treat p-values in these runs as directional screening evidence.
3. Prefer stable moderate gains over brittle high-variance spikes.

## Commands
Primary runner used for these notes:

```bash
PYTHONPATH=src python3 scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl \
  --out-dir docs/research/codex/experiments/phenomenology_run_2026-02-25_n5_full_01 \
  --variants-file docs/research/codex/experiments/phenomenology_variants_2026-02-25.json \
  --top-k-variants 12 \
  --models qwen2.5:1.5b \
  --runs 5 \
  --preset balanced \
  --mode lite
```

## Limits
1. Current findings are sensitive to the rule-based judge.
2. Sample sizes are moderate; they support selection, not final proof.
3. Variant strings are proxies for concepts; wording quality can confound concept quality.
4. Results are time-bound and model-bound.

## Next Validation Steps
1. Re-run top variants on `mistral:7b`.
2. Re-test with an alternate judging backend where feasible.
3. Run ablations on winning variants to isolate active ingredients.

## Session Addendum (2026-02-25T22:49:46Z)

### Session Identity
- Author: Codex (GPT-5 coding agent)
- Session type: different session from prior notes
- Session framing: falsification-first assumption challenge in isolated local outputs, with no runtime behavior edits

### What was run (isolated)
1. `PYTHONPATH=src python3 -u scripts/eval_harness/run_variant_gate.py --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl --out-dir experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n1_smoke --variants-file docs/research/codex/experiments/phenomenology_variants_2026-02-25.json --top-k-variants 3 --models qwen2.5:1.5b --runs 1 --preset balanced --mode lite`
2. `PYTHONPATH=src python3 -u scripts/eval_harness/run_variant_gate.py --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl --out-dir experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n3_full --variants-file docs/research/codex/experiments/phenomenology_variants_2026-02-25.json --top-k-variants 12 --models qwen2.5:1.5b --runs 3 --preset balanced --mode lite`
3. `PYTHONPATH=src python3 -u scripts/eval_harness/run_variant_gate.py --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl --out-dir experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n1_smoke --variants-file docs/research/codex/experiments/phenomenology_variants_2026-02-25.json --top-k-variants 12 --models mistral:7b --runs 1 --preset balanced --mode lite`

### Observations (screening only)
1. `qwen2.5:1.5b` (`runs=3`) showed mixed outcomes: several positive global deltas, but repeated structured-output regressions across many variants.
2. `mistral:7b` (`runs=1`) showed broad positive deltas but with increased latency for most variants; this remains low-confidence due to single-run sampling.
3. Cross-model behavior is not uniform in risk profile (qwen shows structured-output fragility; mistral smoke run does not eliminate transfer uncertainty).

### Interpretation in this session framing
1. These results should be treated as directional evidence for assumption stress-testing, not proof of universal improvement.
2. Promotion should remain blocked pending higher-run cross-model confirmation and alternate-judge checks.
3. This addendum intentionally frames outcomes as falsification pressure on assumptions, not affirmation of theory.

## Session Addendum (2026-02-26T08:31:12Z)

### Session Identity
- Author: Codex (GPT-5 coding agent)
- Session type: different session from earlier entries
- Session framing: assumption-challenge continuation with cross-model confirmation and judge-backend stress test

### New runs and artifacts
1. Cross-model confirmation:
- `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n3_full/summary.md`
2. Alternate judge backend test on fixed outputs:
- Input outputs: `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n3_full/run_results.jsonl`
- Re-judged file: `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n3_full/judged_results_ollama_qwen.jsonl`

### Observations (screening interpretation)
1. `mistral:7b` at `runs=3` shows broad positive deltas vs direct across most variants.
2. Structured-output regressions still appear for some variants (notably `v06_contradiction_probe` in this run).
3. Alternate judge backend execution succeeded technically, but all rows were `ollama_fallback` with low confidence, yielding non-informative constant scores.

### Implication for assumptions
1. Cross-model transfer looks plausible for several variants, but risk is lane-dependent due to structured-output regressions.
2. Judge-dependency remains unresolved because the alternate judge did not produce valid discriminative outputs in this attempt.
3. Current evidence remains directional and selection-oriented, not causal proof.

## Session Addendum (2026-02-26T12:29:24Z)

### Session Identity
- Author: Codex (GPT-5 coding agent)
- Session type: different session from prior entries
- Session framing: high-sample data expansion + resilience hardening for long local eval runs

### New data added
1. `qwen2.5:1.5b` high-sample run:
- `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n8_full/summary.md`
2. `mistral:7b` expanded run:
- `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n5_full/summary.md`
3. Aggregation-ready catalog and handoff:
- `experiments-local/philo_assumption_challenge_2026-02-25/run_catalog.json`
- `experiments-local/philo_assumption_challenge_2026-02-25/run_catalog.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/AGGREGATION_HANDOFF.md`

### Safety/operations additions
1. Added resumable watchdog wrapper for long jobs:
- `experiments-local/philo_assumption_challenge_2026-02-25/resumable_gate_runner.py`
2. Wrapper enforces `--resume` and auto-restarts on prolonged inactivity.

### Observations (screening-level)
1. With `qwen` at `runs=8`, strongest deltas narrowed versus smaller-run snapshots; top signals remain but effect sizes are more moderate.
2. With `mistral` at `runs=5`, several variants remain strongly positive versus direct with consistent sign-test support.
3. Structured-output regressions remain an active concern in `qwen` lanes and should remain gating-critical.

### Interpretation in this session framing
1. Expanded samples reduce small-run optimism risk and are better suited for cross-agent synthesis.
2. Current evidence supports lane-specific recommendations, not universal rollout.
3. This entry is intended to improve aggregate interpretability across multiple researcher sessions.
