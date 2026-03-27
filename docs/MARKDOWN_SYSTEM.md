# Markdown System

## Purpose
Define a simple, durable structure for Markdown documents so research and ops docs remain discoverable and non-duplicative.

## Inputs
- Existing Markdown files in repo root, `docs/`, `docs/research/`, and `experiments-local/`

## Outputs
- Canonical index: `docs/MARKDOWN_INDEX.md`
- Canonical R&D ledger: `docs/research/R_AND_D_LEDGER.md`
- Canonical experiment registry folder: `experiments-local/registry/`
- Archive-candidate review list: `experiments-local/_review/ARCHIVE_CANDIDATES.md`

## Commands
Inventory helper:
```bash
rg --files -g '*.md'
```

## Rules
1. Canonical/project docs must live in `docs/`.
2. Experimental run artifacts must live in `experiments-local/`.
3. Every newly created high-level report must be added to `docs/MARKDOWN_INDEX.md`.
4. Every meaningful experiment run must have its own trace file in `experiments-local/registry/` and an entry in `experiments-local/registry/INDEX.md`.
5. Every meaningful research session must append an entry to `docs/research/R_AND_D_LEDGER.md`.
6. Files are not deleted during cleanup passes; uncertain files go to archive-candidate review first.
7. Naming convention:
- Decision docs: `*_DECISION_*_YYYY-MM-DD.md` or similar explicit date suffix.
- Research snapshots: `*_YYYY-MM-DD.md`.
- Living notes: `*_notes.md` with explicit owner/session context.
- Registry traces: `run_<track>__<run_id>.md`.

## Limits
1. This system improves discoverability but does not by itself resolve semantic conflicts between docs.
2. Archive candidacy is a review signal, not an automatic delete/move action.
