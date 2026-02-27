# Cognitive Infra Validation Program v1 (QuickThink)

## Status
Active research program (cross-agent continuity document).

## Purpose
Build statistically grounded evidence for cognitive-infrastructure scaffolds that improve quality without hidden regressions, while preserving latency and interpretability.

## Intent Alignment
This program is aligned to the user intent:
- treat language as infrastructure,
- test philosophical/hermeneutic concepts as operational controls,
- prioritize reproducible findings over ad-hoc prompt tinkering,
- maintain a continuous research thread with explicit direction and chaptered outputs.

## Overview
Program tracks:
1. Track A - Candidate Confirmation
- Validate strongest variants (`v02`, `v03`) with larger N and per-group gating.
2. Track B - Ablation Attribution
- Isolate which sub-rules of `v02` and `v03` carry the measured lift.
3. Track C - Cross-Model Generalization
- Test whether winning scaffolds transfer across local model lanes.

## Brand Frame
Name: **Cognitive Infra Validation Program (CIVP)**
Motto: **Structure should earn its place by measurable lift.**

## Chapters
### Chapter 1 - Confirmation Under Load
Goal:
- replicate significance with larger paired sample counts.

### Chapter 2 - Group Safety Gate
Goal:
- prevent aggregate improvements from hiding subgroup regressions.

### Chapter 3 - Ablation Truth Test
Goal:
- identify minimal active ingredients in winning variants.

### Chapter 4 - Transfer Test
Goal:
- determine whether improvements are model-specific or portable.

## Inputs
- Prompt subset: `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- Candidate variants: `v02_language_game_moves`, `v03_horizon_fusion_guard`
- Canonical runner: `scripts/eval_harness/run_variant_gate.py`

## Outputs
- Run artifacts (`run_results.jsonl`, `judged_results.jsonl`, `summary.json`, `summary.md`)
- Per-group gate report with wins/losses/ties and p-values
- Ablation report with ranking and retention recommendation
- Shared log entries in `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md`

## Commands
Primary confirmation command template:

```bash
PYTHONPATH=src python3 -u scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl \
  --out-dir <out_dir> \
  --variants-file <variants_file> \
  --top-k-variants <k> \
  --models <model list> \
  --runs 15 \
  --preset balanced \
  --mode lite
```

## Limits
- Rule-based judge is screening-grade, not final proof.
- High tie rates can reduce effective non-tie N in sign tests.
- Findings must be re-checked before runtime default changes.

## Decision Rules
Must:
1. retain variants with positive global delta and non-regressive group profile.
2. prioritize significant results with acceptable latency.
3. reject variants with repeated structured-output regressions unless lane-gated.

May:
1. keep non-significant variants as conditional lanes if lift cases are strategically important.
2. route strict-format classes away from fragile scaffolds.
