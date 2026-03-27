# Variant Deployment Gate

- Prompt set: `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- Variants file: `docs/research/codex/experiments/variants_top2_2026-02-25.json`
- Variants tested: `v02_language_game_moves, v03_horizon_fusion_guard`
- Models: `qwen2.5:1.5b, mistral:7b`
- Runs per prompt: `15`
- Engine mode for variants: `lite`
- Preset: `balanced`
- Strict-direct groups: `(none)`

## qwen2.5:1.5b

| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |
|---|---:|---:|---:|---:|---:|
| direct | 5.572 | 0.000 | 4789.77 | 0.00 | 180 |
| v02_language_game_moves | 5.711 | 0.139 | 3826.96 | -962.81 | 180 |
| v03_horizon_fusion_guard | 5.761 | 0.189 | 3592.19 | -1197.58 | 180 |

### Pairwise vs direct

| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |
|---|---:|---:|---:|---:|---:|
| v02_language_game_moves | 39 | 28 | 113 | 0.582 | 0.2215 |
| v03_horizon_fusion_guard | 38 | 26 | 116 | 0.594 | 0.1686 |

## mistral:7b

| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |
|---|---:|---:|---:|---:|---:|
| direct | 5.461 | 0.000 | 8641.56 | 0.00 | 180 |
| v02_language_game_moves | 6.033 | 0.572 | 9281.65 | 640.09 | 180 |
| v03_horizon_fusion_guard | 6.078 | 0.617 | 8495.97 | -145.60 | 180 |

### Pairwise vs direct

| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |
|---|---:|---:|---:|---:|---:|
| v02_language_game_moves | 88 | 19 | 73 | 0.822 | 0.0000 |
| v03_horizon_fusion_guard | 90 | 17 | 73 | 0.841 | 0.0000 |

## Lift Cases

Cases where direct<=4 and variant>=6 in same prompt/run.

- qwen2.5:1.5b v02_language_game_moves R002#run9: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run10: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run11: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v03_horizon_fusion_guard R002#run12: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v02_language_game_moves R002#run14: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v02_language_game_moves S001#run2: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v03_horizon_fusion_guard S001#run2: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v02_language_game_moves S001#run14: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v03_horizon_fusion_guard S001#run14: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v02_language_game_moves S001#run15: direct=3.0 variant=7.0 delta=4.0
- mistral:7b v03_horizon_fusion_guard S001#run15: direct=3.0 variant=7.0 delta=4.0
- qwen2.5:1.5b v02_language_game_moves R002#run7: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v02_language_game_moves R002#run10: direct=3.0 variant=6.0 delta=3.0
- qwen2.5:1.5b v02_language_game_moves R002#run13: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v03_horizon_fusion_guard R002#run13: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves M001#run2: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves M001#run5: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard M001#run5: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves M001#run7: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard M001#run7: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves M001#run10: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard M001#run10: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard R002#run6: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard R002#run10: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run1: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run1: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run3: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run3: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run4: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run4: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run5: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run5: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run6: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run6: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run7: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run7: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run8: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run8: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run9: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run9: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run10: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run10: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run11: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run11: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run12: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run12: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v02_language_game_moves S001#run13: direct=4.0 variant=7.0 delta=3.0
- mistral:7b v03_horizon_fusion_guard S001#run13: direct=4.0 variant=7.0 delta=3.0
- qwen2.5:1.5b v02_language_game_moves I003#run1: direct=4.0 variant=6.0 delta=2.0
- qwen2.5:1.5b v03_horizon_fusion_guard I003#run1: direct=4.0 variant=6.0 delta=2.0

## Warnings

- group_regression: model=qwen2.5:1.5b mode=v02_language_game_moves group=structured_output score_delta_vs_direct=-0.333
- group_regression: model=qwen2.5:1.5b mode=v03_horizon_fusion_guard group=structured_output score_delta_vs_direct=-0.267
