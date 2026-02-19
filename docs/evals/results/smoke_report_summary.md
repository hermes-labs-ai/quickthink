# Eval Summary

## qwen2.5:1.5b

| mode | avg_score | p50_ms | p95_ms | avg_total_ms |
|---|---:|---:|---:|---:|
| direct | 5.33 | 8583.08 | 11362.83 | 8813.06 |
| lite | 4.00 | 6824.43 | 6896.12 | 4811.50 |
| two_pass | 4.67 | 5073.44 | 5807.17 | 3890.05 |

### lite vs direct

- overall: wins=0 losses=1 ties=2 raw=0.000 non_tie=0.000
- reasoning: wins=0 losses=1 ties=2 raw=0.000 non_tie=0.000

### two_pass vs direct

- overall: wins=1 losses=1 ties=1 raw=0.333 non_tie=0.500
- reasoning: wins=1 losses=1 ties=1 raw=0.333 non_tie=0.500

### lite vs two_pass

- overall: wins=0 losses=2 ties=1 raw=0.000 non_tie=0.000
- reasoning: wins=0 losses=2 ties=1 raw=0.000 non_tie=0.000

