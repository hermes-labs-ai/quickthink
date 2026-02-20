# Open Source Release Readiness Checklist

This checklist is a release gate for publishing `quickthink` as an open source repository.

Status labels:
- `PASS`: ready now
- `PARTIAL`: acceptable for alpha/beta, needs follow-up
- `BLOCKED`: must fix before public release

## A) Legal and policy

- [x] `PASS` Top-level license file exists (`LICENSE`).
- [x] `PASS` Security policy exists (`SECURITY.md`).
- [x] `PASS` Code of conduct exists (`CODE_OF_CONDUCT.md`).
- [x] `PASS` Support guidance exists (`SUPPORT.md`).
- [x] `PASS` Public claims policy exists (`docs/PUBLIC_CLAIMS_POLICY.md`).

## B) Repository hygiene and structure

- [x] `PASS` Runtime source is cleanly isolated in `src/quickthink/`.
- [x] `PASS` Canonical eval harness is separated from legacy helpers:
  - Canonical: `scripts/eval_harness/*`
  - Legacy: `scripts/evals/*`
- [x] `PASS` Private/local artifacts are ignored:
  - `experiments-local/`
  - `docs/evals/results/` (except `README`)
  - `docs/patent/`
  - `hermeslabs-site/`
- [x] `PASS` Docs index exists (`docs/README.md`).

## C) Onboarding and usability

- [x] `PASS` Root README explains purpose/scope and includes copy-paste commands.
- [x] `PASS` First-time setup guide exists (`docs/GETTING_STARTED.md`).
- [x] `PASS` Troubleshooting guide exists (`docs/TROUBLESHOOTING.md`).
- [x] `PASS` README clarifies supported models vs experimental lanes.
- [x] `PASS` Canonical vs legacy script usage is explicitly documented.

## D) Testing and reliability

- [x] `PASS` Local test suite passes:
  - `PYTHONPATH=src .venv/bin/pytest -q`
- [x] `PASS` Syntax/compile sanity passes:
  - `python3 -m compileall -q src scripts tests`
- [x] `PASS` CI workflow exists (`.github/workflows/ci.yml`).
- [ ] `PARTIAL` No integration/e2e tests that require live Ollama in CI yet.

## E) Release process and packaging

- [x] `PASS` Release checklist exists (`docs/release/RELEASE_CHECKLIST.md`).
- [x] `PASS` Release process doc exists (`docs/release/RELEASE_PROCESS.md`).
- [x] `PASS` Changelog exists (`CHANGELOG.md`).
- [x] `PASS` Package metadata exists (`pyproject.toml`).
- [x] `PASS` Manual release-check workflow exists (`.github/workflows/release-check.yml`).
- [ ] `PARTIAL` No automated version/tag enforcement yet (manual process).

## F) Supply-chain and provenance (2026 baseline)

- [ ] `PARTIAL` No provenance attestation artifact published per release yet.
- [ ] `PARTIAL` No SBOM artifact (SPDX/CycloneDX) attached to releases yet.
- [ ] `PARTIAL` No dependency-review PR gate workflow yet.
- [ ] `PARTIAL` No OpenSSF Scorecard monitoring workflow/reporting yet.
- [ ] `PARTIAL` Workflow permission hardening and action pinning policy not fully documented/enforced.
- [x] `PASS` Hash-anchored release freeze/tag process documented and executed.
- [x] `PASS` Baseline standards map exists (`docs/release/SUPPLY_CHAIN_BASELINE_2026.md`).

## G) Evaluation and claims discipline

- [x] `PASS` Canonical eval datasets and rubric docs are present.
- [x] `PASS` Compatibility snapshot includes caveat/context requirements.
- [x] `PASS` Deployment gate criteria documented (`docs/evals/deployment_gate_2026.md`).
- [ ] `PARTIAL` Latency claims still require token-normalized benchmark runs for strict comparability.

## H) UX and product polish

- [x] `PASS` CLI command surface is coherent (`ask`, `bench`, `ui`).
- [ ] `PARTIAL` UI polish is functional but not production-grade.
- [ ] `PARTIAL` `ui_server.py` is monolithic and should be decomposed for long-term maintainability.

## Recommended pre-release follow-ups (non-blocking for alpha)

1. Add one CI smoke integration job that runs a tiny local harness with mocked/fixture responses.
2. Split `src/quickthink/ui_server.py` into:
   - server logic
   - static HTML template
   - client script
3. Add machine/runtime metadata capture into benchmark report output by default.
4. Implement provenance attestations + SBOM release assets.
5. Add dependency-review + scorecard workflows.

## Gate decision

Current gate recommendation: **READY FOR PUBLIC ALPHA**.

Reason:
- No legal/policy blockers remain.
- Onboarding and docs are usable for non-expert contributors.
- Tests and CI exist.
- Remaining items are polish/scale concerns, not release blockers.
