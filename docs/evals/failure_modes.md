# Failure Modes Where Compact Planning Can Harm Output

## 1) Over-constraint Collapse
- Symptom: concise but wrong answer; creativity/coverage drops.
- Typical trigger: too-small plan budget on complex tasks.
- Detect via: correctness drop with low latency gain.

## 2) Protocol Leakage
- Symptom: `[P]` or internal plan appears in user-facing answer.
- Typical trigger: weak extraction or model instruction drift in `lite`.
- Detect via: format/policy violation flags.

## 3) Plan Hallucination Anchoring
- Symptom: model follows a bad compact plan and doubles down.
- Typical trigger: invalid or low-quality plan not repaired well.
- Detect via: high `plan_repaired` + low correctness.

## 4) Format Rigidity Regression
- Symptom: answer obeys plan but misses requested output format details.
- Typical trigger: plan tokens consume attention needed for strict schema tasks.
- Detect via: format-validity score drop in structured_output group.

## 5) Hint Misapplication
- Symptom: stale continuity hint contaminates unrelated prompt.
- Typical trigger: hint always injected, low relevance filtering.
- Detect via: multi_turn_continuity prompts where context shift exists.

## 6) Latency Tail Blow-up (two_pass)
- Symptom: p95/p99 latency spikes despite quality gains.
- Typical trigger: second model call variability and retries.
- Detect via: p95 overhead by mode and route bucket.

## 7) Repair Loop Cost Without Benefit
- Symptom: frequent plan repairs add latency but no quality lift.
- Typical trigger: fragile grammar compliance for specific model.
- Detect via: compare repaired vs non-repaired score deltas.

## 8) Bypass Misrouting
- Symptom: complex tasks incorrectly routed to direct path.
- Typical trigger: simplistic complexity heuristic thresholds.
- Detect via: low route_score on failed reasoning/constraint prompts.

## 9) Verbosity Drift
- Symptom: compact planning still yields verbose final answers.
- Typical trigger: answer prompt under-specifies output length.
- Detect via: verbosity-control failures in instruction_constraints group.

## 10) False Confidence in Win-Rate
- Symptom: apparent quality gains from narrow prompt mix.
- Typical trigger: unbalanced eval set or weak rubrics.
- Detect via: per-group breakdown and confidence intervals.
