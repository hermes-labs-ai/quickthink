# Eval Summary

## qwen2.5:1.5b

| mode | avg_score | p50_ms | p95_ms | avg_total_ms |
|---|---:|---:|---:|---:|
| direct | 4.75 | 8500.07 | 15347.37 | 8063.89 |
| lite | 4.85 | 3754.99 | 14109.56 | 4722.13 |
| two_pass | 4.85 | 3530.27 | 6187.27 | 3644.29 |

### lite vs direct

- overall: wins=4 losses=4 ties=12 raw=0.200 non_tie=0.500
- reasoning: wins=4 losses=4 ties=12 raw=0.200 non_tie=0.500

### two_pass vs direct

- overall: wins=3 losses=2 ties=15 raw=0.150 non_tie=0.600
- reasoning: wins=3 losses=2 ties=15 raw=0.150 non_tie=0.600

### lite vs two_pass

- overall: wins=5 losses=6 ties=9 raw=0.250 non_tie=0.455
- reasoning: wins=5 losses=6 ties=9 raw=0.250 non_tie=0.455

