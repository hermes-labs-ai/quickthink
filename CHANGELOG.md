# Changelog

All notable changes to this project should be documented in this file.

Format follows Keep a Changelog principles and semantic versioning.

## [Unreleased]
### Added
- One-pass `lite` mode with inline `[P]/[A]` protocol and extraction.
- Preset profiles: `fast`, `balanced`, `strict`.
- Eval tooling:
  - `run_sample_eval.py`
  - `judge_pairwise.py`
  - `build_report.py`
  - `compat_matrix_snapshot.py`
- One-command quickstart script: `scripts/demo/quickstart.sh`.
- Release process and release-notes generator.
- Repository publishability audit:
  - `docs/release/REPO_STRUCTURE_AND_PUBLISHABILITY_AUDIT_2026-02-20.md`

### Changed
- CLI supports preset selection and compatibility/preset listing.

### Fixed
- Python 3.9 compatibility for dataclass usage.
