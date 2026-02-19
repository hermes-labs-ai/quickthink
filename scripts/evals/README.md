# Legacy Eval Helpers (Smoke / Demo)

Status: **non-canonical**.

This folder contains lightweight helper scripts that are still useful for quick smoke checks and ad-hoc demos.

Canonical batch evaluation pipeline is now:
- `scripts/eval_harness/run_suite.py`
- `scripts/eval_harness/judge_suite.py`
- `scripts/eval_harness/validate_judged_results.py`
- `scripts/eval_harness/report_suite.py`

Use this folder when you need:
- very fast local smoke checks
- one-off report rendering experiments

Do not use `scripts/evals/*` as source-of-truth for published benchmark claims.
