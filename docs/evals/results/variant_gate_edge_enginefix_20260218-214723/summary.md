# Variant Deployment Gate

- Prompt set: `docs/evals/prompt_set_edge_cases.jsonl`
- Variants file: `experiments-local/pipeline1-runs/20260218-212527-pipeline1-cycle/selected_variants.json`
- Variants tested: `lite_v4_check_step, lite_v1_constraint_first`
- Models: `qwen2.5:1.5b, llama3.2:latest`
- Runs per prompt: `2`
- Engine mode for variants: `lite`
- Preset: `balanced`

## qwen2.5:1.5b

| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |
|---|---:|---:|---:|---:|---:|
| direct | 5.167 | 0.000 | 1481.89 | 0.00 | 48 |
| lite_v1_constraint_first | 5.229 | 0.062 | 1416.65 | -65.24 | 48 |
| lite_v4_check_step | 5.229 | 0.062 | 1436.62 | -45.27 | 48 |

### Pairwise vs direct

| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |
|---|---:|---:|---:|---:|---:|
| lite_v4_check_step | 7 | 3 | 38 | 0.700 | 0.3438 |
| lite_v1_constraint_first | 6 | 3 | 39 | 0.667 | 0.5078 |

## llama3.2:latest

| mode | avg_score | score_delta_vs_direct | avg_latency_ms | latency_delta_vs_direct_ms | rows |
|---|---:|---:|---:|---:|---:|
| direct | 5.604 | 0.000 | 1617.10 | 0.00 | 48 |
| lite_v1_constraint_first | 5.667 | 0.062 | 1481.94 | -135.15 | 48 |
| lite_v4_check_step | 5.688 | 0.083 | 1647.81 | 30.71 | 48 |

### Pairwise vs direct

| mode | wins | losses | ties | non_tie_win_rate | sign_test_pvalue |
|---|---:|---:|---:|---:|---:|
| lite_v4_check_step | 5 | 5 | 38 | 0.500 | 1.0000 |
| lite_v1_constraint_first | 3 | 2 | 43 | 0.600 | 1.0000 |

## Lift Cases

Cases where direct<=4 and variant>=6 in same prompt/run.

- llama3.2:latest lite_v4_check_step E010#run1: direct=4.0 variant=7.0 delta=3.0
- llama3.2:latest lite_v1_constraint_first E010#run1: direct=4.0 variant=7.0 delta=3.0
- llama3.2:latest lite_v4_check_step E003#run1: direct=4.0 variant=6.0 delta=2.0
