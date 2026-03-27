# OSS Readiness Scorecard (2026-02-25)

This scorecard evaluates `quickthink` for public OSS release readiness on a 0-10 scale.

Scoring model:
- `0-3`: not publishable
- `4-6`: early internal/beta
- `7-8`: public alpha quality
- `9+`: strong OSS launch quality

## Rubric and scores

| Category | Weight | Score | Notes |
|---|---:|---:|---|
| Repository structure and clarity | 15% | 9.0 | Runtime, canonical eval harness, and docs are clearly segmented. |
| Onboarding and docs UX | 20% | 8.8 | README + getting-started + troubleshooting are strong and copy-paste friendly. |
| Testing and CI reliability | 20% | 8.7 | Unit tests pass; CI matrix + compile checks are in place; no live integration lane in CI yet. |
| Supply chain and workflow security | 15% | 9.0 | SHA-pinned actions, dependency review, scorecard, SBOM/provenance workflows configured. |
| Release discipline and governance | 10% | 8.8 | Release checklist/process/changelog present; version/tag automation still manual. |
| Product UX and polish | 10% | 8.2 | Functional UI flow; `ui_server.py` remains monolithic for long-term maintainability. |
| Agent-readability and maintainability metadata | 10% | 9.2 | `AGENTS.md` added with canonical paths, commands, and guardrails. |

**Weighted overall score (baseline lens): 8.8 / 10**

**Adversarial-adjusted score (recommended for go/no-go discipline): 8.3 / 10**

Current release stance: **Publishable for public alpha**, but not yet at a conservative `9+` bar.

## Evidence snapshot

- Local tests: `PYTHONPATH=src .venv/bin/pytest -q` => `19 passed`
- Compile sanity: `python3 -m compileall -q src scripts tests`
- Workflows present:
  - `.github/workflows/ci.yml`
  - `.github/workflows/dependency-review.yml`
  - `.github/workflows/scorecard.yml`
  - `.github/workflows/release-supply-chain.yml`
  - `.github/workflows/release-check.yml`
- Repo docs/guidance:
  - `README.md`
  - `docs/GETTING_STARTED.md`
  - `docs/TROUBLESHOOTING.md`
  - `docs/release/OPEN_SOURCE_RELEASE_READINESS_CHECKLIST.md`

## Gaps to reach 9+

1. Add one CI smoke integration lane with deterministic fixture responses for harness scripts.
2. Split `src/quickthink/ui_server.py` into server/template/client modules.
3. Execute one release dry-run and confirm SBOM + provenance artifacts are attached and discoverable.
4. Add top-of-README badges after default branch is finalized.

## Delta from prior state

- Added agent-facing repository contract: `AGENTS.md`
- Added automated dependency updates: `.github/dependabot.yml`
- Updated stale release checklist items to reflect implemented workflows.
