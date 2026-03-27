# Compatibility Matrix

Generated: 2026-02-18T18:50:26+00:00

Interpretation status: historical snapshot only.
Do not use this table as a standalone headline performance claim.
Use canonical harness reports with full environment metadata and token-limit controls for publication-grade comparisons.

Supported models: `qwen2.5:1.5b`, `mistral:7b`, `gemma3:27b`.

| Model | Preset | Direct p50 | Lite p50 | Lite p95 | Lite overhead p50 | Two-pass p50 | Status |
|---|---|---:|---:|---:|---:|---:|---|
| qwen2.5:1.5b | balanced | 2690.67 | 3905.50 | 3905.50 | 1214.83 | 7742.86 | WARN |
| mistral:7b | balanced | 3523.49 | 294.40 | 294.40 | -3229.10 | 2949.86 | PASS |
| gemma3:27b | balanced | 40287.19 | 6125.02 | 6125.02 | -34162.17 | 6127.54 | PASS |

Notes:
- Status PASS means lite overhead meets target thresholds on snapshot prompts.
- Re-generate with: `python3 scripts/evals/compat_matrix_snapshot.py`.
- This snapshot is environment-scoped, not universal. Always publish the following context with any claim:
  - hardware/runtime details
  - prompt set and subset size
  - run count/repeats
  - generation limits/settings (for example token caps, preset, mode set)
  - evaluation date and git SHA
- Interpret large positive/negative overhead deltas cautiously; output-length differences can confound latency.
