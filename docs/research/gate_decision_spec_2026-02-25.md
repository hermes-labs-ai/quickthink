# Gate Decision Spec (2026-02-25)

## Purpose
Define a minimal but robust gate-decision output for QuickThink that classifies each lane as `PASS`, `FAIL`, or `INCONCLUSIVE`, while keeping rubric scoring auditable and improvable.

## Inputs
- Canonical judged results:
  - `scripts/eval_harness/judge_suite.py` outputs
  - `scripts/eval_harness/validate_judged_results.py` validated JSONL
- Canonical report summaries:
  - `scripts/eval_harness/report_suite.py` outputs
- Variant gate outputs:
  - `scripts/eval_harness/run_variant_gate.py` summary + warnings
- Gate thresholds (source of truth):
  - `docs/evals/deployment_gate_2026.md`

## Outputs
Produce one machine-readable decision artifact per run:
- File path (recommended):
  - `docs/evals/results/gate_decision-<timestamp>.json`
- Per lane key:
  - `(task_class, model_family)`
- Decision enum:
  - `PASS`
  - `FAIL`
  - `INCONCLUSIVE`
- Required fields:
  - `quality_non_tie_win_rate`
  - `quality_sign_test_pvalue`
  - `latency_delta_ms_vs_direct`
  - `lift_cases`
  - `group_regressions`
  - `sample_size_rows`
  - `decision_reason`

Example shape:
```json
{
  "run_id": "shared_scaffold_gate_strict2_20260225-193357",
  "threshold_profile": "deployment_gate_2026",
  "lanes": [
    {
      "task_class": "strict_format",
      "model_family": "qwen",
      "decision": "INCONCLUSIVE",
      "metrics": {
        "quality_non_tie_win_rate": 0.565,
        "quality_sign_test_pvalue": 0.678,
        "latency_delta_ms_vs_direct": -700.29,
        "lift_cases": 5,
        "group_regressions": ["instruction_constraints"]
      },
      "sample_size_rows": 48,
      "decision_reason": "Latency good; significance and strict-group regression gate not satisfied."
    }
  ]
}
```

## Decision Logic (Boolean + Ternary)
Boolean gate (strict):
- `PASS` only if all required thresholds are met.
- Else `FAIL`.

Recommended practical gate (ternary):
- `PASS`: thresholds met and sample size minimum met.
- `FAIL`: thresholds violated with adequate sample size.
- `INCONCLUSIVE`: insufficient sample size, unstable backend run, or mixed/contradictory evidence.

Rationale:
- A ternary label prevents overconfident `FAIL` when infra instability (for example Ollama stalls) blocks reliable evidence.

## Task Taxonomy (Routing + Reporting)
Required task classes:
1. `strict_format`
2. `reasoning`
3. `continuity`

Mapping:
- Prompt-set `group` values map to task classes.
- Gate and routing both consume the same task class label.

## Rubric Quality: Is Current Taxonomy Good Enough?
Current rubric is good as `v1` operationally, but should be iterated.

Why it is usable now:
- Clear 4 dimensions (correctness, constraint adherence, format validity, verbosity).
- Composite score and tie-break rules already defined.

Why it should be improved:
- Some strict-format failures are currently under/over-penalized depending on judge heuristics.
- Composite averages can hide catastrophic failures in one dimension.

## Rubric Iteration Plan
1. Add critical-failure flags:
- `hard_format_violation` (boolean)
- `hard_constraint_violation` (boolean)
- If either true on strict-format tasks, force lane decision to non-pass.

2. Add confidence calibration field:
- `judge_confidence` already exists; aggregate and report confidence distribution per lane.

3. Add adjudication slice:
- Human review on a small sampled set of disagreements (for example 20 cases per lane) to calibrate judge drift.

4. Add stability checks:
- Compare decision across two reruns; downgrade to `INCONCLUSIVE` if direction flips.

## Commands
Current run/report commands (existing):
```bash
PYTHONPATH=src .venv/bin/python scripts/eval_harness/run_variant_gate.py ...
PYTHONPATH=src .venv/bin/python scripts/eval_harness/report_suite.py ...
```

Future gate command (proposed):
```bash
PYTHONPATH=src .venv/bin/python scripts/eval_harness/make_gate_decision.py \
  --summary-json <path>/summary.json \
  --judged-jsonl <path>/judged_results.jsonl \
  --threshold-profile deployment_gate_2026 \
  --out docs/evals/results/gate_decision-<timestamp>.json
```

## Limits
- Gate quality is only as good as judged-row validity and prompt-set representativeness.
- Backend instability can distort outcomes; such runs must be marked `INCONCLUSIVE`.
- Do not publish universal claims from a single lane or single hardware environment.

## Next Steps
1. Implement `make_gate_decision.py` with ternary output and per-lane keys.
2. Add `task_class` to run/judged rows at generation time.
3. Wire gate decision artifact into release docs/checklist.
4. Add strict-format hard-failure flags in judge output and gate logic.
