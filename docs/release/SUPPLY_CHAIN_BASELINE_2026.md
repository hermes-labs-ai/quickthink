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

## Current repo status (2026-02-20)

- `PASS`: hash-anchored release freeze/tag process exists and has been executed.
- `PARTIAL`: CI and release workflows exist, but no published provenance attestation workflow yet.
- `PARTIAL`: no first-class SBOM release artifact pipeline yet.
- `PARTIAL`: no dedicated dependency-review workflow yet.
- `PARTIAL`: no Scorecard workflow/reporting yet.
- `PARTIAL`: workflow action pinning policy is not fully enforced.

## Conservative next actions

1. Add SBOM generation + upload in release workflow.
2. Add dependency-review workflow for pull requests.
3. Add provenance attestation generation + verification for release artifacts.
4. Add OpenSSF Scorecard workflow and track score trends.
5. Apply least-privilege `permissions:` to all workflows and document pinning rules.

## Notes on claims

Do not claim compliance with any framework by name unless all required controls are implemented and verified in CI artifacts.
