# Thread Recovery Map (2026-02-27)

## Purpose
Reconstruct a clean, decision-grade project context after lost chat threads, and define the next research execution loop.

## Inputs
- `AGENTS.md`
- `FOLDER_MAP.md`
- `docs/AGENT_BOOTSTRAP.md`
- `docs/MARKDOWN_INDEX.md`
- `docs/research/R_AND_D_LEDGER.md`
- `docs/research/DECISION_GATES.md`
- `docs/research/MODEL_DEFAULTS_AND_GUARDRAILS_2026-02-26.md`
- `docs/research/instruction_lane_iterative_loop_2026-02-27.md`
- `experiments-local/registry/INDEX.md`
- `experiments-local/registry/run_philo_assumption_challenge__run_*.md` (recent instruction-lane traces)
- `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md`

## Outputs
- Canonical restart state for research orchestration.
- Prioritized open loops with clear next actions.
- Initial agent operational rules for multi-assistant coordination.

## Recovered Ground Truth
1. Repo/root:
- Canonical repo root is `/Users/rolibosch/Documents/QuickThink`.
- `/Users/rolibosch/Documents/New project` is an alias symlink.

2. Current strategic posture:
- Keep model-lane-specific defaults; no universal scaffold default.
- Default objective tier is `balanced`; `no-loss-first` is an explicit stricter option.
- Use `docs/research/DECISION_GATES.md` as normative thresholds.

3. Model-default snapshot (current):
- `qwen2.5:1.5b`: default `v02_language_game_moves` (`high` confidence).
- `mistral:7b`: default `v01_anchor_dual_relation` (`high` confidence).
- `llama3.1:8b`: default `v02_language_game_moves` (`medium-high`) with lane fallback.
- `gemma2:9b`: default `v01_anchor_dual_relation` (`low-medium`) with reasoning fallback.
- `claude-haiku-4-5`: keep direct lane; scaffold variants still regress instruction constraints.

4. Active unresolved loops:
- qwen instruction-lane confirmation run (`run_qwen15_v11_instr_n8`) was incomplete and needs a fresh completion pass.
- mistral instruction-lane rerun remains pending after earlier instability.
- haiku instruction-lane scaffold attempts have not passed promotion gates.

## Open Questions To Resolve Next
1. Can `qwen` instruction-lane `v11` pass at larger N without structured-output regressions?
2. Can `mistral` instruction-lane variants replicate positive lift in a stable run?
3. Should Anthropic instruction-lane work continue on Haiku, or pause and test a higher-tier model lane?

## Commands
```bash
# Baseline checks
PYTHONPATH=src .venv/bin/pytest -q
python3 -m compileall -q src scripts tests

# Research hygiene
scripts/check_research_hygiene.sh

# Canonical eval harness pattern (example)
PYTHONPATH=src python3 scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl \
  --out-dir experiments-local/philo_assumption_challenge_2026-02-25/<run_id> \
  --variants-file <variants.json> \
  --top-k-variants 2 --models <model_name> --runs <n> --mode lite --preset balanced --request-timeout-s 180
```

## Multi-Agent Operational Rules (v1)
1. One canonical source for state:
- Research state must be written to ledger + registry, not kept only in chat.

2. Single writer for a run:
- Only one assistant owns a given `run_id` and `out-dir`; others review/read only.

3. Strict closeout gates per session:
- Update `experiments-local/registry/INDEX.md`.
- Update relevant `experiments-local/registry/run_*.md`.
- Append `docs/research/R_AND_D_LEDGER.md`.
- Update `docs/MARKDOWN_INDEX.md` for major new docs.
- Run `scripts/check_research_hygiene.sh` and record PASS/FAIL.

4. Recommendation labels are mandatory:
- Every rollout recommendation must include one of:
  - `PROMOTE`
  - `PROMOTE_WITH_GUARDRAILS`
  - `HOLD`
  - `REJECT`

5. Rules quality standard:
- Rules must be objective, testable, and auditable from files.
- If a rule cannot be checked from artifacts, it is guidance, not a rule.

## Immediate Next Research Queue
1. Re-run qwen instruction validator confirmation (`v11`) to completion with a fresh run directory.
2. Re-run mistral instruction-lane variants (`v10/v11`) at stable N.
3. Decide Haiku lane policy for next cycle (`direct-only` hold vs higher-tier Anthropic probe).

## Limits
- This file is a recovery snapshot for 2026-02-27 and can drift as new runs complete.
- Some prior conclusions are small-to-medium N and model-version scoped.
