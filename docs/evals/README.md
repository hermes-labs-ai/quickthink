# Eval Suite

This folder contains a lightweight, model-agnostic evaluation package for `quickthink`.

## Files
- `prompt_set.jsonl`: 120 prompts with required fields:
  - `prompt_id`
  - `group`
  - `prompt`
  - `expected_rubric`
  - `pass_fail_checklist`
- `scoring_rubrics.md`: 0-2 scoring rubric for correctness, constraint adherence, format validity, verbosity control.
- `harness_spec.md`: A/B/C execution and reporting specification.
- `failure_modes.md`: common regressions caused by compact planning.

## Group Breakdown
- reasoning: 30
- structured_output: 30
- instruction_constraints: 30
- multi_turn_continuity: 30

## Notes
- Prompts are intentionally short and portable across model providers.
- Rubrics are property-based (no gold strings), suited for manual or judge-model scoring.

## Quality Gates
- Validate the canonical dataset before any run:
  - `python3 scripts/evals/validate_prompt_set.py --path docs/evals/prompt_set.jsonl`
- Validate run JSONL before UI ingestion or scoring:
  - `python3 scripts/evals/validate_results.py --path <results.jsonl> --expected-prompts 120 --expected-runs 3 --models qwen2.5:1.5b mistral:7b gemma3:27b`

## Canonical Pipeline
- Runner: `scripts/eval_harness/run_suite.py`
- Judge: `scripts/eval_harness/judge_suite.py`
- Judge validation: `scripts/eval_harness/validate_judged_results.py`
- Report: `scripts/eval_harness/report_suite.py`

`scripts/evals/*` is smoke/demo support only.
