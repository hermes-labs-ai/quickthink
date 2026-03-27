# Variant Deployment Gate

- Prompt set: `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- Variants file: `docs/research/codex/experiments/phenomenology_variants_top3_2026-02-25.json`
- Variants tested: `v02_language_game_moves, v03_horizon_fusion_guard, v04_negative_capability`
- Models: `qwen2.5:1.5b`
- Runs per prompt: `15`
- Engine mode for variants: `lite`
- Preset: `balanced`
- Strict-direct groups: `(none)`

## qwen2.5:1.5b

| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |
|---|---:|---:|---:|---:|---:|
| direct | 5.544 | 0.000 | 2199.68 | 0.00 | 180 |
| v02_language_game_moves | 5.839 | 0.294 | 1617.45 | -582.23 | 180 |
| v03_horizon_fusion_guard | 5.778 | 0.233 | 1480.61 | -719.07 | 180 |
| v04_negative_capability | 5.700 | 0.156 | 1716.84 | -482.84 | 180 |

### Pairwise vs direct

| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |
|---|---:|---:|---:|---:|---:|
| v02_language_game_moves | 45 | 21 | 114 | 0.682 | 0.0043 |
| v03_horizon_fusion_guard | 39 | 22 | 119 | 0.639 | 0.0396 |
| v04_negative_capability | 44 | 29 | 107 | 0.603 | 0.1006 |

## Lift Cases

Cases where direct<=4 and variant>=6 in same prompt/run.

- qwen2.5:1.5b v02_language_game_moves R002#run8: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v02_language_game_moves R002#run11: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run11: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v04_negative_capability R002#run11: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v02_language_game_moves R002#run5: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run5: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v04_negative_capability R002#run5: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v02_language_game_moves R002#run6: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run6: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v04_negative_capability R002#run6: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v03_horizon_fusion_guard R003#run15: direct=3.0 variant=6.0 delta=3.0
- qwen2.5:1.5b v04_negative_capability I001#run8: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run2: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run3: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run3: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run3: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run4: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run4: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run5: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run5: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run6: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run6: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run8: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run10: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run11: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run13: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run13: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v04_negative_capability I003#run13: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run14: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v02_language_game_moves I003#run15: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run15: direct=4.0 variant=6.0 delta=2.0

## Warnings

- group_regression: model=qwen2.5:1.5b mode=v04_negative_capability group=structured_output score_delta_vs_direct=-0.467
