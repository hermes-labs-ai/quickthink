# Instruction Lane Iteration Plan (2026-02-27)

## 1. Purpose
Define a repeatable loop to improve instruction-format reliability across models, using recent Haiku/qwen results and pending mistral data.

## 2. Current Findings
- Haiku 4.5: instruction-focused scaffolds remain negative vs direct; regress in instruction/structured_output.
- qwen2.5:1.5b: v10/v11 lift scores and cut latency; v11 avoids structured_output regression.
- Mistral: current run stalled (54/144 rows); no summary yet.

## 3. Hypotheses
- H1: Instruction regressions on Haiku stem from format over-constraining; needs explicit echo + validate JSON step.
- H2: v11-style validator generalizes to small qwen/mistral with low risk.
- H3: Latency wins from trimmed scaffolds are portable; accuracy depends on lane-specific constraints.

## 4. Next Experiments
- E1 (Haiku): design JSON-echo validator scaffold; n=4; success gate: no negative delta in instruction_constraints and win_rate>=0.6.
- E2 (Mistral): rerun instruction lane v10/v11 fresh n=4; if blocked, drop to n=2 for smoke to confirm direction.
- E3 (Qwen confirm): qwen1.5b v11 at n=8 to firm up CI; add structured_output guard if any regression appears.

## 5. Gating Criteria
- Promotion: delta>=0, instruction_constraints win_rate>=0.6, no new structured_output regressions, latency not worse than +150ms.
- Hold/direct: any negative group delta or win_rate<0.5.

## 6. Orchestration Loop
1) Plan: select lane+model, pick variant, define n and gate.
2) Run: `run_variant_gate.py` with one out_dir per run; avoid overlapping processes.
3) Record: update registry trace + ledger + live notes immediately after completion.
4) Check: run `scripts/check_research_hygiene.sh` + pytest.
5) Decide: apply gating; queue next variant/model.

## 7. Data Hygiene Rules
- One run_dir per attempt; no re-use. Use `_v2` suffix if needed.
- Registry entry only when summary exists; partial runs are noted in live notes, not registry.
- All runs must have summary.md/json and judged_results.jsonl.

## 8. Risks
- API variance (Haiku) may mask small gains; keep n>=4.
- Process contention (multiple run_variant_gate) can stall; enforce one active process per model.
- Structured_output regressions can slip through if gating ignores group deltas.

## 9. Resource/Budget
- Haiku n=4 ~ few dollars; qwen/mistral local cost = time/thermal only.
- Target cycle time per run: <15 minutes.

## 10. Roles/Defaults
- Instruction lane default candidate (local): qwen v11_instruction_validator, pending n=8 confirm.
- Haiku default: direct-only until a scaffold clears gates.
- Mistral: TBD after clean run.

## 11. Timeline
- Today: complete mistral n=4 clean run; draft Haiku JSON-echo variant and run n=4.
- Next: qwen v11 confirmation n=8; roll into model_routing_policy if passes gates.

## 12. Open Decisions
- Whether to spend budget on Anthropic Sonnet/Opus for instruction lane.
- Whether to adopt a global instruction-lane scaffold or keep per-model defaults.
