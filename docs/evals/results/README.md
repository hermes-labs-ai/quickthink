# Eval Results Output

This folder stores generated artifacts from `scripts/eval_harness`.

## Expected files
- `run_results.jsonl`: raw run outputs (A/B/C)
- `run_manifest.json`: reproducibility metadata (git sha, dataset sha, run config)
- `judged_results.jsonl`: per-row rubric scores
- `report_summary.json`: machine-readable summary metrics
- `report_summary.md`: human-readable report
