# Maintenance Notes - 2026-02-18

Scope: no major code changes; review-only notes for security/readiness/consolidation planning.

## Quick Health
- Tests: `19 passed`.
- Core runtime appears stable.
- Canonical eval harness exists and is documented.

## Security / Safety Observations
1. Secret-pattern scan found no confirmed hardcoded keys, but produced false-positive hits inside model output artifacts.
   - Action later: treat `docs/evals/results/*` as generated data and avoid scanning those in secret checks.
2. No repo-level security policy files found (`SECURITY.md`, `CODEOWNERS`, `CONTRIBUTING`, `LICENSE`).
   - Action later: add minimum GitHub trust/compliance docs before public exposure.
3. No CI/workflow directory detected (`.github/workflows/*`).
   - Action later: add basic CI (tests + validators + lightweight security check).
4. Dependency-health tooling not present in venv (`pip-audit`, `bandit`, `safety` not installed).
   - Action later: choose one and add optional script/CI gate.

## Consistency / Robustness Risks
1. **Mode mismatch risk**:
   - `scripts/eval_harness/run_suite.py` includes default mode `direct_think`.
   - Legacy validator `scripts/evals/validate_results.py` allows only `direct|lite|two_pass`.
   - Potential effect: default canonical runs may fail legacy validation or produce confusing mixed expectations.
   - Suggested decision later: either align validators or isolate `direct_think` runs to separate pipeline/output.
2. `src/quickthink/ui_server.py` remains very large (~1300 lines), combining UI assets + API handlers + run orchestration.
   - Action later: split into handler module(s) + static template resource.

## GitHub Readiness Notes
1. Decide what is source-of-truth vs generated artifacts:
   - Source: docs/specs/scripts/src/tests
   - Generated: `docs/evals/results/*` and many experiment outputs.
2. Consider policy:
   - Keep only milestone artifacts in repo.
   - Move transient run outputs to ignored artifact dir or release attachments.
3. Add clear public posture docs:
   - `LICENSE`
   - `SECURITY.md`
   - `CONTRIBUTING.md`
   - `.github/workflows/ci.yml`

## Operational Notes
- `.gitignore` currently ignores `experiments-local/` (good), but not `docs/evals/results/`.
- There is at least one `.lock` file artifact in results/experiment paths; decide if lock files should remain ephemeral and ignored.

## Suggested Next Maintenance Pass (no major refactor)
1. Add a tiny `docs/NOW.md` with canonical commands/paths only.
2. Add public metadata files (`LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`).
3. Add CI smoke workflow for tests + prompt/results validators.
4. Decide on generated artifact retention + git policy.
5. Resolve mode mismatch (`direct_think`) policy before broad sharing.
