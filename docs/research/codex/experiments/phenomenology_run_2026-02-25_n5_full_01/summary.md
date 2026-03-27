# Variant Deployment Gate

- Prompt set: `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- Variants file: `docs/research/codex/experiments/phenomenology_variants_2026-02-25.json`
- Variants tested: `v01_anchor_dual_relation, v02_language_game_moves, v03_horizon_fusion_guard, v04_negative_capability, v05_curvature_first, v06_contradiction_probe, v07_boundary_literalism, v08_continuity_memory_light, v09_adversarial_paraphrase_resilience, v10_minimal_commitment, v11_repair_then_realize, v12_constraint_priority_order`
- Models: `qwen2.5:1.5b`
- Runs per prompt: `5`
- Engine mode for variants: `lite`
- Preset: `balanced`

## qwen2.5:1.5b

| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |
|---|---:|---:|---:|---:|---:|
| direct | 5.667 | 0.000 | 2759.45 | 0.00 | 60 |
| v01_anchor_dual_relation | 5.717 | 0.050 | 1473.58 | -1285.88 | 60 |
| v02_language_game_moves | 5.750 | 0.083 | 1828.92 | -930.54 | 60 |
| v03_horizon_fusion_guard | 5.783 | 0.117 | 2178.94 | -580.51 | 60 |
| v04_negative_capability | 5.817 | 0.150 | 1898.68 | -860.77 | 60 |
| v05_curvature_first | 5.600 | -0.067 | 1707.19 | -1052.26 | 60 |
| v06_contradiction_probe | 5.617 | -0.050 | 1793.81 | -965.64 | 60 |
| v07_boundary_literalism | 5.717 | 0.050 | 1955.15 | -804.30 | 60 |
| v08_continuity_memory_light | 5.583 | -0.083 | 2160.47 | -598.98 | 60 |
| v09_adversarial_paraphrase_resilience | 5.617 | -0.050 | 2041.03 | -718.43 | 60 |
| v10_minimal_commitment | 5.600 | -0.067 | 2023.40 | -736.05 | 60 |
| v11_repair_then_realize | 5.633 | -0.033 | 1970.20 | -789.25 | 60 |
| v12_constraint_priority_order | 5.633 | -0.033 | 1926.70 | -832.75 | 60 |

### Pairwise vs direct

| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |
|---|---:|---:|---:|---:|---:|
| v01_anchor_dual_relation | 10 | 11 | 39 | 0.476 | 1.0000 |
| v02_language_game_moves | 15 | 13 | 32 | 0.536 | 0.8506 |
| v03_horizon_fusion_guard | 13 | 12 | 35 | 0.520 | 1.0000 |
| v04_negative_capability | 15 | 11 | 34 | 0.577 | 0.5572 |
| v05_curvature_first | 14 | 16 | 30 | 0.467 | 0.8555 |
| v06_contradiction_probe | 13 | 12 | 35 | 0.520 | 1.0000 |
| v07_boundary_literalism | 13 | 12 | 35 | 0.520 | 1.0000 |
| v08_continuity_memory_light | 10 | 14 | 36 | 0.417 | 0.5413 |
| v09_adversarial_paraphrase_resilience | 14 | 16 | 30 | 0.467 | 0.8555 |
| v10_minimal_commitment | 13 | 15 | 32 | 0.464 | 0.8506 |
| v11_repair_then_realize | 11 | 13 | 36 | 0.458 | 0.8388 |
| v12_constraint_priority_order | 10 | 11 | 39 | 0.476 | 1.0000 |

## Lift Cases

Cases where direct<=4 and variant>=6 in same prompt/run.

- qwen2.5:1.5b v05_curvature_first S001#run2: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v01_anchor_dual_relation R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v02_language_game_moves R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v05_curvature_first R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v07_boundary_literalism R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v08_continuity_memory_light R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v12_constraint_priority_order R002#run3: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v07_boundary_literalism I003#run1: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v10_minimal_commitment I003#run1: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v12_constraint_priority_order I003#run1: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run2: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v05_curvature_first I003#run2: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v07_boundary_literalism I003#run2: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v08_continuity_memory_light I003#run2: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v11_repair_then_realize I003#run2: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run3: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run3: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v10_minimal_commitment I003#run3: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v01_anchor_dual_relation I003#run5: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run5: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v05_curvature_first I003#run5: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v07_boundary_literalism I003#run5: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v09_adversarial_paraphrase_resilience R002#run3: direct=4.0 variant=6.0 delta=2.0

## Warnings

- group_regression: model=qwen2.5:1.5b mode=v01_anchor_dual_relation group=instruction_constraints score_delta_vs_direct=-0.267
- group_regression: model=qwen2.5:1.5b mode=v02_language_game_moves group=instruction_constraints score_delta_vs_direct=-0.267
- group_regression: model=qwen2.5:1.5b mode=v05_curvature_first group=structured_output score_delta_vs_direct=-0.733
- group_regression: model=qwen2.5:1.5b mode=v06_contradiction_probe group=instruction_constraints score_delta_vs_direct=-0.333
- group_regression: model=qwen2.5:1.5b mode=v06_contradiction_probe group=structured_output score_delta_vs_direct=-0.667
- group_regression: model=qwen2.5:1.5b mode=v08_continuity_memory_light group=structured_output score_delta_vs_direct=-0.467
- group_regression: model=qwen2.5:1.5b mode=v09_adversarial_paraphrase_resilience group=instruction_constraints score_delta_vs_direct=-0.267
- group_regression: model=qwen2.5:1.5b mode=v09_adversarial_paraphrase_resilience group=structured_output score_delta_vs_direct=-0.467
- group_regression: model=qwen2.5:1.5b mode=v10_minimal_commitment group=instruction_constraints score_delta_vs_direct=-0.267
- group_regression: model=qwen2.5:1.5b mode=v10_minimal_commitment group=structured_output score_delta_vs_direct=-0.933
- group_regression: model=qwen2.5:1.5b mode=v11_repair_then_realize group=instruction_constraints score_delta_vs_direct=-0.400
- group_regression: model=qwen2.5:1.5b mode=v12_constraint_priority_order group=instruction_constraints score_delta_vs_direct=-0.267
- group_regression: model=qwen2.5:1.5b mode=v12_constraint_priority_order group=structured_output score_delta_vs_direct=-0.400
