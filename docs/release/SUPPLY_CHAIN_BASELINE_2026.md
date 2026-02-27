# Supply-Chain Baseline (2026)

This document defines a conservative, public-open-source release baseline for `quickthink`, aligned to current widely adopted guidance.

## External standards references

- SLSA provenance and verification guidance: https://slsa.dev/
- OpenSSF Scorecard checks and automation: https://github.com/ossf/scorecard
- CISA minimum elements for an SBOM: https://www.cisa.gov/sbom
- SPDX specification and tooling ecosystem: https://spdx.dev/
- GitHub artifact attestation guidance: https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations
- GitHub dependency review action: https://github.com/actions/dependency-review-action
- NIST SSDF (secure software development framework): https://csrc.nist.gov/Projects/ssdf

## 2026 baseline controls

1. Provenance attestations for release artifacts.
2. SBOM generated and shipped with each release (SPDX or CycloneDX).
3. Dependency risk gate on pull requests (dependency review).
4. Scorecard monitoring enabled for repository security posture drift.
5. Least-privilege GitHub Actions permissions and reviewed third-party actions policy.
6. Signed/tagged immutable release practice with reproducible release notes and hashes.

## Current repo status (2026-02-25)

- `PASS`: hash-anchored release freeze/tag process exists and has been executed.
- `PASS`: provenance attestation workflow configured (`.github/workflows/release-supply-chain.yml`).
- `PASS`: SBOM generation workflow configured (`.github/workflows/release-supply-chain.yml`).
- `PASS`: dependency-review workflow configured (`.github/workflows/dependency-review.yml`).
- `PASS`: Scorecard workflow configured (`.github/workflows/scorecard.yml`).
- `PASS`: workflow actions are SHA pinned.
- `PARTIAL`: first public release still needs one executed dry-run confirming SBOM/provenance artifacts are attached and retrievable.

## Conservative next actions

1. Execute one release dry-run and verify SBOM/provenance artifact discoverability.
2. Capture verification evidence in `docs/release/RELEASE_NOTES_DRAFT.md` (or release notes body).
3. Keep least-privilege workflow `permissions:` under periodic review.
4. Track scorecard trend over at least 2 weekly runs before public claims.

## Notes on claims

Do not claim compliance with any framework by name unless all required controls are implemented and verified in CI artifacts.
