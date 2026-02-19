# Consolidation Prep Notes (Post-Qwen Optimization)

Context: keep code changes minimal until Qwen optimization pass is finalized. This note is a cleanup runway for the consolidator.

## Snapshot (current)
- Core runtime is functional and tests pass.
- Canonical benchmark path exists: `scripts/eval_harness/*`.
- Sprawl concentration is mostly in docs/results/experiment artifacts, not core runtime logic.

## Main Consolidation Risks
1. Duplicate workflow surfaces (`scripts/evals/*` vs `scripts/eval_harness/*`) creating operator confusion.
2. Generated artifacts mixed with source docs (`docs/evals/results/*`, `docs/agent-comms/*`).
3. Very large UI adapter file (`src/quickthink/ui_server.py`) mixing UI assets and server logic.
4. Experiment directories (`experiments-local/*`) lack a single index and retention policy.

## Freeze-Now Rules (until optimization complete)
1. No large file moves.
2. No canonical-path changes.
3. New experiment artifacts must stay under `experiments-local/` only.
4. New benchmark artifacts must stay under `docs/evals/results/` only.
5. If adding new docs, include one-line purpose at top and owner/date.

## Recommended Consolidation Options

### Option A: Lean Product Layout (lowest cognitive load)
- Keep only one active flow per concern.
- Move generated artifacts out of docs into `artifacts/`.
- Keep docs limited to stable specs and operator guides.

### Option B: Product + Lab Split (recommended)
- `product/` mindset: runtime + canonical eval harness + release docs.
- `lab/` mindset: experiments, variant search, exploratory notes.
- Promote from lab to product only when manifest + validation + summary exist.

### Option C: Time-Boxed Archive Sweep
- Keep current tree, but archive by date and add index registry.
- Fastest to execute but preserves more historical clutter.

## Proposed First Cleanup Pass (safe)
1. Add `docs/NOW.md` as single source of truth for current canonical paths.
2. Mark all non-canonical scripts/docs as `archive` or `smoke-only` in headers.
3. Create `experiments-local/INDEX.md` with run_id, purpose, winner, promoted?(y/n).
4. Move stale reports to dated archive folder.
5. Create retention policy: keep only latest + milestone artifacts in active paths.

## Consolidator Checklist
- [ ] Confirm canonical runner/judge/report paths.
- [ ] Confirm where generated artifacts should live long-term.
- [ ] Build one mapping table: "keep / archive / delete / merge".
- [ ] Split `ui_server.py` into UI template, handlers, and runner adapter modules.
- [ ] Re-run tests and one smoke eval after moves.

## Decision Requests For Owner
1. Choose consolidation target layout (A/B/C above).
2. Decide whether `hermeslabs-site/` stays in this repo or is split out.
3. Decide artifact retention horizon (e.g., keep 14 days active, archive rest).

