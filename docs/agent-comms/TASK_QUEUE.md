# Task Queue (Conservative)

## T1 - Eval Ingestion API (UI agent)
- Goal: Add read-only endpoint(s) to load `docs/evals/prompt_set.jsonl` and results JSONL.
- Scope: parsing + pagination + error reporting only.
- Done when: UI can browse prompts and results without modifying eval files.

## T2 - Preflight Validator Hook (UI agent)
- Goal: Run `validate_prompt_set.py` before eval execution starts.
- Scope: call script, display pass/fail and sha256.
- Done when: execution is blocked on failed preflight.

## T3 - Results Validator Hook (runner agent)
- Goal: Validate run output with `validate_results.py` before scoring.
- Scope: schema/coverage checks only.
- Done when: invalid runs are rejected with actionable errors.

## T4 - Judge Output Schema (eval agent)
- Goal: Define strict JSON schema for judge decisions (winner/confidence/reason).
- Scope: schema + validator script + one sample file.
- Done when: malformed judge outputs fail fast.

## T5 - Reproducible Run Metadata (infra agent)
- Goal: capture run manifest (`git_sha`, model tag, mode, date, dataset sha).
- Scope: one JSON manifest per run.
- Done when: every run can be reproduced from metadata.
