# Integration Hardening Report (2026-02-25)

## Purpose
Summarize implementation hardening, integration verification depth, and residual risks after introducing lane-policy routing and gate-decision artifacts.

## Inputs
- Runtime changes:
  - `src/quickthink/config.py`
  - `src/quickthink/routing.py`
  - `src/quickthink/engine.py`
  - `src/quickthink/cli.py`
- Eval-harness changes:
  - `scripts/eval_harness/run_variant_gate.py`
  - `scripts/eval_harness/make_gate_decision.py`
- Tests:
  - `tests/test_engine_lane_policy.py`
  - `tests/test_cli_lane_policy.py`
  - `tests/test_make_gate_decision.py`
  - existing runtime/harness tests
- Documentation:
  - `README.md`
  - `docs/research/gate_decision_spec_2026-02-25.md`
- Research context:
  - `docs/research/codex/philosophy/philo_researcher_1_notes.md`
  - `docs/research/codex/philosophy/phenomenology_significance_report_2026-02-25.md`

## Outputs
### Integration checks completed
1. Unit-level behavior checks:
- strict-safe lane policy routes strict-format prompts to direct path.
- default lane policy preserves scaffold path.
- CLI invalid lane-policy option is rejected.
- gate-decision script handles all-tie lanes as `INCONCLUSIVE`.

2. End-to-end CLI smoke check (live local backend):
- `quickthink ask ... --lane-policy strict_safe --show-route`
- observed route output confirmed strict-safe direct fallback path.

3. Eval-harness decision artifact generation:
- `gate_decision.json` produced from run/judged artifacts with explicit PASS/FAIL/INCONCLUSIVE semantics.

### Philosophy-research compatibility check
- Existing philosophy notes assert no single variant dominates all groups and recommend lane-specific routing.
- Current production direction (task-lane fallback + per-model/per-purpose handling) is consistent with those findings.

## Commands
Validation commands executed:
```bash
PYTHONPATH=src .venv/bin/pytest -q
python3 -m compileall -q src scripts tests
```

Live CLI smoke executed:
```bash
PYTHONPATH=src .venv/bin/python -m quickthink.cli ask \
  'json only: {"ok":true,"why":"short"}' \
  --model qwen2.5:1.5b \
  --lane-policy strict_safe \
  --show-route
```

## Limits
- Concurrent Ollama usage by other agents can cause long blocking calls in variant runs.
- `qwen3:4b` still shows unstable/stalled behavior in long-run harness jobs and remains inconclusive.
- Gate thresholds are intentionally strict and may classify promising lanes as `FAIL` when sample slice lacks required lift counts.

## Residual Risks
1. Backend stall handling remains partial:
- request timeout alone does not fully prevent long socket waits under contention.

2. Strict-task classifier is heuristic:
- current regex-based `infer_task_class` may miss edge prompts.

3. UX discoverability:
- lane policy exists in CLI/docs, but no explicit guidance matrix by use case in quick help output yet.

## Next Hardening Steps
1. Add retry/backoff + per-call deadline handling in Ollama client path for better stall resilience.
2. Add run checkpointing in `run_variant_gate.py` (incremental writes) to avoid losing long-run progress.
3. Expand task classifier tests with additional strict-format prompt fixtures.
4. Add a tiny "recommended lane policy" table in CLI help/docs (`default` vs `strict_safe` by task type).
