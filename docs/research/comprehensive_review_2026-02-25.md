# Comprehensive Review (2026-02-25)

## Purpose
Consolidate current branch hardening status, integration findings, and lane-gate evidence without changing runtime behavior beyond already approved routing controls.

## Inputs
- Runtime/UI:
  - `src/quickthink/ui_server.py`
  - `src/quickthink/engine.py`
  - `src/quickthink/routing.py`
  - `src/quickthink/cli.py`
- Eval artifacts:
  - `experiments-local/results/shared_scaffold_gate_stable2_20260225-135515/*`
  - `experiments-local/results/shared_scaffold_gate_strict2_20260225-193357/*`
  - `experiments-local/results/shared_scaffold_gate_lanefallback2_20260225-201305/*`
- Philosophy/research references:
  - `docs/research/codex/philosophy/phenomenology_significance_report_2026-02-25.md`
  - `docs/research/integration_hardening_report_2026-02-25.md`

## Outputs
### Implemented now
1. UI supports lane policy (`default`, `strict_safe`) for:
   - single prompt run
   - compare 3 modes (`/api/ask-all`)
2. Backend validates and forwards `lane_policy` in UI API path.
3. Added targeted unit tests:
   - `tests/test_ui_lane_policy.py`
4. Refreshed gate decision artifacts for completed runs:
   - `stable2` and `strict2`.

### Validation status
- `PYTHONPATH=src .venv/bin/pytest -q` -> pass
- `python3 -m compileall -q src scripts tests` -> pass
- targeted post-change tests -> pass (`7 passed`)

## Gate Snapshot
Decisions from `make_gate_decision.py` with `--backend-stable`:

1. `shared_scaffold_gate_stable2_20260225-135515`
- FAIL: 18
- INCONCLUSIVE: 0

2. `shared_scaffold_gate_strict2_20260225-193357`
- FAIL: 8
- INCONCLUSIVE: 0

3. `shared_scaffold_gate_lanefallback2_20260225-201305`
- FAIL: 12
- INCONCLUSIVE: 6

Interpretation:
- strict-direct fallback changed strict-format lane classification from FAIL to INCONCLUSIVE (`no_non_tie_pairs`), removing prior confounded comparisons.
- shared variants still fail continuity/reasoning gate thresholds under current strict deployment criteria, despite directional score improvements in summary reports.

## Risks
1. Contention risk:
- multiple concurrent Ollama eval jobs can skew latency/stability and cause stalls.

2. Classifier risk:
- `infer_task_class` is regex-based and may miss strict prompts outside current patterns.

3. Gate conservatism:
- high tie rates + lift-case minimums can fail promising lanes.

## Recommendations
Must:
1. Keep lane-specific rollout strategy; do not promote a universal shared scaffold.
2. Run next clean eval only when no parallel variant jobs are active.
3. Keep strict-format tasks on `strict_safe` (direct first) while measuring continuity/reasoning lanes separately.

May:
1. Tune gate profile for exploratory runs (separate from deployment gate), then re-check with strict gate.
2. Expand strict-task classifier fixtures before changing routing semantics.

## Commands
```bash
PYTHONPATH=src .venv/bin/pytest -q
python3 -m compileall -q src scripts tests

PYTHONPATH=src .venv/bin/python scripts/eval_harness/make_gate_decision.py \
  --runs-jsonl experiments-local/results/shared_scaffold_gate_stable2_20260225-135515/run_results.jsonl \
  --judged-jsonl experiments-local/results/shared_scaffold_gate_stable2_20260225-135515/judged_results.jsonl \
  --out experiments-local/results/shared_scaffold_gate_stable2_20260225-135515/gate_decision.json \
  --backend-stable
```

## Limits
This review intentionally avoided launching conflicting inference workloads while other agents were running large eval jobs.
