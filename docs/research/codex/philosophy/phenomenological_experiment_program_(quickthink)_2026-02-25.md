# Phenomenological Experiment Program (QuickThink) - 2026-02-25

## Status
Exploratory research plan. Not a runtime behavior change.

## Purpose
Define 10+ concept experiments with useful sample sizes to evaluate whether language-structuring concepts improve QuickThink outcomes.

## Inputs
- Prompt subset: `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- Concept variants: `docs/research/codex/experiments/phenomenology_variants_2026-02-25.json`
- Canonical runner: `scripts/eval_harness/run_variant_gate.py`

## Outputs
- Paired score deltas vs direct mode per concept variant.
- Sign-test p-values per variant.
- Lift cases for failure-to-success transitions.
- Prioritized shortlist of concepts for deeper iteration.

## Experiment Matrix
1. `v01_anchor_dual_relation`
2. `v02_language_game_moves`
3. `v03_horizon_fusion_guard`
4. `v04_negative_capability`
5. `v05_curvature_first`
6. `v06_contradiction_probe`
7. `v07_boundary_literalism`
8. `v08_continuity_memory_light`
9. `v09_adversarial_paraphrase_resilience`
10. `v10_minimal_commitment`
11. `v11_repair_then_realize`
12. `v12_constraint_priority_order`

## N Design
- Prompts: `12` (balanced across 4 groups)
- Runs per prompt: `5`
- Model lane: `qwen2.5:1.5b`
- Paired observations per variant vs direct: up to `60`

Interpretation note:
- `N=60` per variant is moderate; useful for directional ranking and candidate selection.
- This is not a final confirmatory study across all models.

## Commands
Primary run:

```bash
PYTHONPATH=src python3 scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl \
  --out-dir docs/research/codex/experiments/phenomenology_run_2026-02-25 \
  --variants-file docs/research/codex/experiments/phenomenology_variants_2026-02-25.json \
  --top-k-variants 12 \
  --models qwen2.5:1.5b \
  --runs 5 \
  --preset balanced \
  --mode lite
```

## Analysis Protocol
- Must rank variants by:
  - mean score delta vs direct
  - non-tie win rate vs direct
  - sign-test p-value
- May flag variants with strong lift cases despite neutral mean if they rescue repeated failure modes.
- Must reject variants with consistent group-level regressions.

## 2-Week Research Cadence
Week 1:
1. Run the 12-variant lane above.
2. Keep top 4 variants by paired performance + stability.
3. Run sensitivity sweep on top 4 (`fast`, `balanced`, `strict`).

Week 2:
1. Re-test top 2 on second model lane (`mistral:7b`).
2. Run ablation on winning variant (remove one concept at a time).
3. Draft integration recommendation with rollback criteria.

## Limits
- Results depend on current rule-based judge heuristics.
- Concept strings are proxies; poor phrasing can understate concept value.
- Cross-model generalization is not established until Week 2.
