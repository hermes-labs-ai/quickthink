# Agent Joint MD (QuickThink)

## Purpose
Coordinate concurrent agent experiments to prevent resource contention and result contamination while preserving a continuous research thread.

## Scope
Applies to all agents running local eval/variant experiments in this repo.

## Experiment Locking
Must:
1. Announce run intent in `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md` before launch.
2. Include model(s), prompt set, out_dir, N, and expected duration.
3. Check active eval processes (`run_variant_gate.py`, `run_suite.py`) before launch.
4. If another run uses overlapping model resources, either queue or explicitly mark as non-comparable.

May:
1. Run in parallel only when model sets do not overlap.
2. Run in parallel when measuring throughput under contention intentionally (must label this).

## Contamination Policy
Must:
1. Treat latency as contaminated when overlapping model lanes are active.
2. Treat quality as provisional if timeouts/retries occur during contention.
3. Restart critical confirmation runs in isolation before claiming significance.

## Naming Convention
Use out_dir names with:
- `track`, `purpose`, `model`, `N`, date stamp.
Example:
- `civp_trackA_top2_n15_qwen_mistral_2026-02-25`

## Chaptering Convention
All major updates should reference CIVP chapter:
- Chapter 1: confirmation under load
- Chapter 2: group safety gate
- Chapter 3: ablation truth test
- Chapter 4: transfer test

## Shared Notes Requirement
After each meaningful run, append timestamped entry to:
- `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md`

Entry must include:
- Purpose
- Inputs
- Outputs
- Key findings
- Limits

## Commands
Process check:

```bash
ps -ef | rg 'run_variant_gate.py|run_suite.py' | rg -v rg
```

## Limits
This document coordinates process hygiene only. It does not define product behavior changes.
