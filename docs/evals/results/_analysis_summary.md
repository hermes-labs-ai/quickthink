# Eval Summary

## qwen2.5:1.5b

| mode | avg_score | p50_ms | p95_ms | avg_total_ms |
|---|---:|---:|---:|---:|
| direct | 5.41 | 883.75 | 8704.64 | 2453.91 |
| lite | 5.35 | 860.22 | 5458.24 | 1733.78 |

### lite vs direct

- overall: wins=29 losses=29 ties=235 raw=0.099 non_tie=0.500
- instruction_constraints: wins=1 losses=3 ties=86 raw=0.011 non_tie=0.250
- multi_turn_continuity: wins=4 losses=7 ties=12 raw=0.174 non_tie=0.364
- reasoning: wins=20 losses=12 ties=58 raw=0.222 non_tie=0.625
- structured_output: wins=4 losses=7 ties=79 raw=0.044 non_tie=0.364

