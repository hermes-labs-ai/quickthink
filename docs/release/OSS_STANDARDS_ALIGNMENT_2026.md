# OSS Standards Alignment (2026)

This document maps `quickthink` against practical 2026 open-source conventions and security baseline guidance.

## External references used

- OpenSSF Scorecard (project and checks overview): <https://scorecard.dev/>
- OpenSSF best-practice policy example (scorecard threshold framing): <https://best.openssf.org/SCM-BestPractices/github/repository/scorecard_score_too_low.html>
- GitHub artifact provenance attestation action: <https://github.com/actions/attest-build-provenance>
- GitHub Dependabot config reference: <https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file>
- SLSA provenance concepts (supply-chain provenance model): <https://slsa.dev/spec/v1.1/provenance>

## Alignment snapshot

| Area | Convention | quickthink status |
|---|---|---|
| Community health files | License, Code of Conduct, Contributing, Security, Support | Aligned |
| CI baseline | Push/PR tests + compile checks | Aligned |
| Supply chain hardening | SHA-pinned actions, dependency review, scorecard | Aligned |
| Provenance and SBOM | Release-time SBOM + artifact attestation | Configured (needs first public release execution confirmation) |
| Dependency hygiene | Dependabot for workflows and Python dependencies | Aligned |
| README quality | Clear scope, quickstart, architecture map, troubleshooting links | Aligned |
| Agent-readability | Explicit agent contract with canonical paths and commands | Aligned (`AGENTS.md`) |
| Integration confidence | Live end-to-end CI lane with runtime dependency | Partial |
| UI maintainability | Large UI server decomposition for long-term maintainability | Partial |

## Practical interpretation

- Repository is in strong **public-alpha** shape.
- Remaining gaps are not policy blockers; they are mostly engineering polish and long-horizon maintainability items.
- Highest-value next step before “9+ launch quality”: run one release dry-run and verify SBOM/provenance artifacts are attached and retrievable.
