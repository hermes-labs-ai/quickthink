# Deployment Gate (2026)

This defines a stricter go/no-go gate for releasing scaffold variants.

## Why this gate exists

Small-model improvements can look strong on one slice and regress on another. We need:

- paired comparisons against `direct`
- repeated trials
- explicit edge-case prompts
- significance checks, not only average score deltas

## Recommended Process

1. Run broad baseline suite on canonical prompts:
   - `docs/evals/prompt_set.jsonl`
2. Run focused edge-case suite:
   - `docs/evals/prompt_set_edge_cases.jsonl`
3. Evaluate top candidate variants from Pipeline 1 via:
   - `scripts/eval_harness/run_variant_gate.py`
4. Approve only if candidate beats `direct` on both quality and latency with non-trivial confidence.

## Suggested Gates

- Quality:
  - non-tie win-rate vs `direct` >= `0.55`
  - sign-test p-value <= `0.10` (exploratory) or <= `0.05` (strict)
- Latency:
  - avg latency delta vs `direct` <= `-100ms` for small models
- Robustness:
  - edge-case suite must not show systematic formatting/constraint collapse
  - at least 5 concrete `direct fail -> scaffold pass` lift cases

## Edge-Case Pass/Fail Definition

For `docs/evals/prompt_set_edge_cases.jsonl`, a candidate is **PASS** only if all are true:

- Non-tie win-rate vs direct >= `0.55`
- Sign-test p-value <= `0.10`
- Avg latency delta vs direct <= `-50ms`
- Lift cases >= `5`
- No per-group regression warning where score delta <= `-0.25`

Otherwise mark **FAIL** and keep candidate in experiment lane only.

## Pipeline 1 Linkage

- Pipeline 1 output folder pattern:
  - `experiments-local/pipeline1-runs/<timestamp>-pipeline1-cycle/`
- Expected selector artifacts:
  - `selected_variants.json`
  - `selection_debug.json`
  - `PIPELINE1_REPORT.md`

Use `selected_variants.json` as the source of top candidates for gate runs.

## Commands

```bash
# Canonical suite (existing)
.venv/bin/python scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --models qwen2.5:1.5b llama3.2:latest \
  --modes direct lite two_pass \
  --runs 2 \
  --out docs/evals/results/canonical_run.jsonl \
  --manifest-out docs/evals/results/canonical_manifest.json

# Judge + report
.venv/bin/python scripts/eval_harness/judge_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --results docs/evals/results/canonical_run.jsonl \
  --out docs/evals/results/canonical_judged.jsonl \
  --backend rule

.venv/bin/python scripts/eval_harness/report_suite.py \
  --runs docs/evals/results/canonical_run.jsonl \
  --judged docs/evals/results/canonical_judged.jsonl \
  --out-json docs/evals/results/canonical_summary.json \
  --out-md docs/evals/results/canonical_summary.md

# Variant gate on Pipeline 1 winners (top 2 by default)
.venv/bin/python scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/evals/prompt_set_edge_cases.jsonl \
  --models qwen2.5:1.5b llama3.2:latest \
  --runs 2 \
  --out-dir docs/evals/results/variant_gate_edge
```

## External References (2024-2026 direction)

- HELM (standardized, multi-metric evaluation framing):
  - https://crfm.stanford.edu/helm/
- LiveBench (contamination-resistant LLM benchmark framing):
  - https://arxiv.org/abs/2406.19314
- SWE-bench (real task grounding; shows why pass/fail task outcomes matter):
  - https://www.swebench.com/
- SWE-bench Verified announcement (stronger reliability framing):
  - https://openai.com/index/introducing-swe-bench-verified/
- Chain-of-thought prompting baseline context:
  - https://arxiv.org/abs/2201.11903
- Test-time scaling (reasoning tokens) context:
  - https://arxiv.org/abs/2501.19393

These references motivate robust, paired, multi-metric gates rather than single aggregate scores.
