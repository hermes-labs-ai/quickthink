# Eval Suite Handoff

This eval package is ready for downstream agents. Do not modify prompt content unless explicitly requested.

## Source Files
- `docs/evals/prompt_set.jsonl` (120 prompts; canonical dataset)
- `docs/evals/scoring_rubrics.md` (0-2 rubric per dimension)
- `docs/evals/harness_spec.md` (A/B/C run and metric spec)
- `docs/evals/failure_modes.md` (known compact-planning regressions)
- `docs/evals/README.md` (overview)

## Expected Modes
- A: `direct`
- B: `lite`
- C: `two_pass`

## Required Metrics
- latency (p50, p95, overhead vs A)
- token usage (where available)
- win-rate (raw + non-tie)

## Quick Validation
- Prompt count: 120
- Group split: 30 reasoning, 30 structured_output, 30 instruction_constraints, 30 multi_turn_continuity
- Prompt IDs are unique

## Agent Task Boundary
- Treat `prompt_set.jsonl` as locked input.
- Write outputs to a separate folder (recommended: `docs/evals/results/`).
- Keep run logs machine-readable (JSONL).

## Execution Pipeline (Isolated Harness)
- Runner: `scripts/eval_harness/run_suite.py`
- Judge: `scripts/eval_harness/judge_suite.py`
- Report: `scripts/eval_harness/report_suite.py`
- Judge output validation: `scripts/eval_harness/validate_judged_results.py`

## Canonical Decision
- Canonical benchmark path for published claims: `scripts/eval_harness/*`
- `scripts/evals/*` is smoke/demo-only and should not be used as source-of-truth for public metrics.

### Commands
```bash
./.venv/bin/python scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --out docs/evals/results/run_results.jsonl \
  --manifest-out docs/evals/results/run_manifest.json \
  --runs 3
```

```bash
./.venv/bin/python scripts/eval_harness/judge_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --results docs/evals/results/run_results.jsonl \
  --out docs/evals/results/judged_results.jsonl \
  --backend rule
```

```bash
./.venv/bin/python scripts/eval_harness/validate_judged_results.py \
  --path docs/evals/results/judged_results.jsonl
```

```bash
./.venv/bin/python scripts/eval_harness/report_suite.py \
  --runs docs/evals/results/run_results.jsonl \
  --judged docs/evals/results/judged_results.jsonl \
  --out-json docs/evals/results/report_summary.json \
  --out-md docs/evals/results/report_summary.md
```
