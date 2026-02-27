# Research Hygiene Protocol

## Purpose
Prevent documentation drift so registry/ledger/policy files remain living infrastructure rather than one-time artifacts.

## Required check
Run before closing meaningful research sessions:
```bash
scripts/check_research_hygiene.sh
```

## Pass condition
- Script returns `research_hygiene_check=PASS`.

## If failed
1. Fix missing or broken references.
2. Update canonical files in place.
3. Re-run hygiene check.

## Canonical files enforced
- `docs/research/R_AND_D_LEDGER.md`
- `experiments-local/registry/INDEX.md`
- `experiments-local/operations/model_routing_policy_v1.json`
- `docs/research/MODEL_DEFAULTS_AND_GUARDRAILS_2026-02-26.md`
