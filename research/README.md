# QuickThink Research

QuickThink was the starting point for all Hermes Labs scaffold research. These are the experiments that specifically tested the QuickThink (S1) compressed planning scaffold.

## History
QuickThink → scaffold experiments (Studies 001-011) → scaffold independence thesis → prompt optimizer

The full experimental archive lives in [scaffold-independence](https://github.com/roli-lpci/scaffold-independence). This folder contains copies of the studies that specifically tested S1 (QuickThink).

## Studies

- **RESULTS-SUMMARY-002c.md** — Model-specific edge cases. QuickThink rescues 0.8B on two-step classification (0/3 → 3/3) and 9B on multi-hop logic (0/3 → 3/3).
- **RESULTS-SUMMARY-002d.md** — Coding gap analysis. QuickThink tier jumps confirmed: 0.8B + S1 = 1.5B raw on list flattening and code functions.
- **RESULTS-SUMMARY-003.md** — Gap tasks and routing table. Maps which scaffold works for which task type. QuickThink recommended for multi-step reasoning and code generation.

## Key QuickThink Findings
- Rescues complete failures on multi-step reasoning (0/3 → 3/3)
- Creates tier jumps: 0.8B + QuickThink ≥ 1.5B raw
- Should NOT be stacked with other scaffolds (Study 008g showed stacking hurts)
- Best for: multi-step reasoning, constraint satisfaction, code generation
- Not useful for: simple tasks, summarization, binary classification (adds overhead without benefit)
