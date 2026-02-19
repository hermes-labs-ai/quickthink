# A/B/C Harness Spec

## Modes
- A = `direct` (planning bypass forced)
- B = `lite` (one-pass inline protocol)
- C = `two_pass` (separate planning then answer)

## Models
Run each mode on:
- `qwen2.5:1.5b`
- `mistral:7b`
- `gemma3:27b`

## Prompt Set
- Source: `docs/evals/prompt_set.jsonl`
- Total prompts: 120
- Groups: reasoning (30), structured_output (30), instruction_constraints (30), multi_turn_continuity (30)

## Execution Plan
1. For each model, run all prompts in A/B/C.
2. Use `runs=3` per prompt per mode (different seeds/temperatures if available; otherwise repeated calls).
3. Store one JSONL record per execution with:
- `timestamp`
- `model`
- `mode`
- `prompt_id`
- `group`
- `run_index`
- `answer`
- `plan` (if available)
- `plan_repaired`
- `bypassed`
- `route_score`
- `selected_plan_budget`
- `plan_latency_ms`
- `answer_latency_ms`
- `total_latency_ms`
- `token_usage_prompt` (if provider supports)
- `token_usage_completion` (if provider supports)

## Scoring Workflow
1. Score each response on 4 dimensions from `docs/evals/scoring_rubrics.md`.
2. Compute composite score (0-8).
3. Compute pairwise wins per prompt-run:
- B vs A
- C vs A
- B vs C

## Metrics to Report
- Latency:
  - p50/p95 `total_latency_ms` per mode
  - overhead vs A for B and C
- Token usage:
  - average extra prompt/completion tokens vs A
  - average inferred plan tokens for B/C
- Quality:
  - average composite score per mode
  - win-rate vs A (raw and non-tie)
  - per-group win-rate

## Acceptance Gates (from project goals)
- B p50 overhead <= 80ms
- B p95 overhead <= 200ms
- Quality win-rate (B or C vs A) >= 8-15%
- Avg extra plan tokens <= 12 for tiny models

## Lightweight CLI Mapping
- Single prompt timing baseline:
  - `quickthink bench "<prompt>" --model <model> --runs 3`
- Full suite runner should call `quickthink ask` in three configurations:
  - A: `--mode lite` + force bypass (`adaptive_routing=False`, very high bypass threshold)
  - B: `--mode lite`
  - C: `--mode two_pass`

## Reporting Format
Create one summary table per model:
- `mode`
- `avg_score`
- `p50_ms`
- `p95_ms`
- `avg_tokens`
- `win_rate_vs_A`

Also include one failure table:
- `prompt_id`
- `mode`
- `failure_type`
- `short_note`
