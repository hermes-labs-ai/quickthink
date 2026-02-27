# AGENTS.md

Agent-facing operating notes for this repository.

## Project intent

`quickthink` is a local LLM inference-control layer with:
- runtime package in `src/quickthink/`
- canonical evaluation harness in `scripts/eval_harness/`
- docs and release process under `docs/`

Primary goal for agent edits: improve maintainability, docs clarity, and release safety without changing runtime behavior unless explicitly requested.

## Canonical paths

- Runtime code: `src/quickthink/`
- Canonical eval pipeline: `scripts/eval_harness/`
- Legacy helpers (non-canonical): `scripts/evals/`
- Tests: `tests/`
- Release docs: `docs/release/`

## Shared research notes path

- Canonical cross-agent research log must be updated at:
  - `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md`
- Project-local pointer path (symlink target):
  - `experiments-local/RESEARCH_NOTES_LIVE.md`
- Agents must append a timestamped entry after meaningful research runs and market snapshots.

## Commands

Use these before proposing completion:

```bash
PYTHONPATH=src .venv/bin/pytest -q
python3 -m compileall -q src scripts tests
```

Automatic enforcement (must):
- Git hooks under `.githooks/` are canonical local guardrails.
- `pre-commit` must run `scripts/check_research_hygiene.sh`.
- `pre-push` must run pytest + compileall + research hygiene.
- Agents working in this repo must ensure `core.hooksPath=.githooks` is set for the local clone.

## Guardrails

- Do not change eval scoring semantics or runtime model behavior for cleanup-only work.
- Treat `scripts/eval_harness/*` as source of truth over `scripts/evals/*`.
- Keep user-facing claims bounded; avoid adding universal or guaranteed-performance language.
- Preserve pinned GitHub Actions SHAs when editing workflow files.

## Agent-readable outputs

When writing docs/reports:
- prefer explicit section headers (`Purpose`, `Inputs`, `Outputs`, `Commands`, `Limits`)
- include exact file paths and command examples
- separate normative guidance (`must`) from optional guidance (`may`)
- avoid hidden assumptions (state environment and prerequisites)

## Workspace hygiene

- Canonical repo root must be treated as:
  - `/Users/rolibosch/Documents/QuickThink`
- Human-facing alias for the repo may exist at:
  - `/Users/rolibosch/Documents/Apps & Codes/QuickThink` (symlink to canonical repo)
- Agents must prefer project-local paths for new artifacts:
  - docs/reports in `docs/` or `experiments-local/`
  - research run artifacts in `experiments-local/`
- Avoid creating new top-level folders outside the canonical repo unless explicitly asked.
- Before writing new docs/artifacts, agents should check `FOLDER_MAP.md` for current path conventions.

## Markdown governance

- Before creating a new high-level `.md` report, check `docs/MARKDOWN_INDEX.md` for an existing canonical target.
- When adding a new high-level `.md`, update `docs/MARKDOWN_INDEX.md` in the same change.
- If a file appears stale or duplicative, add it to `experiments-local/_review/ARCHIVE_CANDIDATES.md` instead of deleting it directly.

## R&D assembly line (mandatory)

For any meaningful research/eval session, agents must do all of the following before completion:
1. Register runs in `experiments-local/registry/INDEX.md` and create/update one per-run trace file in `experiments-local/registry/`.
2. Append a session entry to `docs/research/R_AND_D_LEDGER.md`.
3. Ensure important new docs are listed in `docs/MARKDOWN_INDEX.md`.
4. If stale/duplicate docs are discovered, add them to `experiments-local/_review/ARCHIVE_CANDIDATES.md`.

5. Apply thresholds from `docs/research/DECISION_GATES.md` when making rollout recommendations.
6. Complete `docs/SESSION_CLOSEOUT_CHECKLIST.md` before ending a meaningful research session.
7. Run `scripts/check_research_hygiene.sh` and ensure PASS before session closeout.

Operational requirement:
- Do not keep decision-relevant outcomes only in chat; write them to repository markdown artifacts above.


## Session bootstrap (for new agents)

At the start of a new session in this repo, read the following in order:
1. `AGENTS.md`
2. `FOLDER_MAP.md`
3. `docs/AGENT_BOOTSTRAP.md`
4. `docs/MARKDOWN_INDEX.md`
5. `docs/research/R_AND_D_LEDGER.md`
6. `experiments-local/registry/INDEX.md`

Optional helper:
- `scripts/agent_bootstrap.sh`

## Authoritative storage contract (do not fork)

Use only these canonical destinations for ongoing research operations:
1. Cross-session interpretation log:
- `docs/research/R_AND_D_LEDGER.md`

2. Experiment registry (one trace per run):
- `experiments-local/registry/INDEX.md`
- `experiments-local/registry/run_*.md`

3. Machine-readable routing/default policy:
- `experiments-local/operations/model_routing_policy_v1.json`

4. Human-readable default/guardrail policy:
- `docs/research/MODEL_DEFAULTS_AND_GUARDRAILS_2026-02-26.md`

5. Shared cross-agent live notes:
- `/Users/rolibosch/Documents/codex folder/research/quickthink/RESEARCH_NOTES_LIVE.md`

Hard rules:
- Do not create alternative registry folders or alternate ledger files.
- Do not create duplicate policy files with new names when updating existing policies.
- Update the canonical file in place and append timestamped entries where applicable.
- If a new canonical file is truly required, record the migration reason in `docs/research/R_AND_D_LEDGER.md` and update `docs/MARKDOWN_INDEX.md` in the same change.
