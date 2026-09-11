# Changelog

All notable changes to this project should be documented in this file.

Format follows Keep a Changelog principles and semantic versioning.

## [Unreleased]

### Added
- `quickthink ask --dry-run` resolves routing and prints the exact prompt(s) that would be sent to Ollama without contacting it, so routing can be inspected offline.
- `QuickThinkEngine.preview()` exposes the same network-free routing preview to library users.
- CI runs `ruff check` and tests Python 3.13.

### Changed
- `pydantic` was declared as a runtime dependency but never imported; it is no longer installed with the package.

### Fixed
- `quickthink ask --mode direct` is accepted by the CLI (the engine already supported it; the CLI only allowed `lite` and `two_pass`).
- `quickthink bench` measures its `direct` column with the real `direct` mode instead of a `lite` configuration forced to bypass.
- `quickthink ask` and `quickthink bench` exit with code 2 and a short hint when Ollama is unreachable, instead of an `httpx` traceback.

## [0.2.1] - 2026-08-04

### Added
- `quickthink --version` reports the installed package version.

### Changed
- Prepare the first PyPI publication through a tag-bound GitHub Actions trusted-publisher workflow. The workflow verifies that the tag and package version match, builds distributions, and checks them before the protected PyPI environment can publish.
- Make source installation before publication and package installation after publication explicit in the quickstart.
- Synchronize package, citation, and Zenodo release metadata for `0.2.1`.

## [0.2.0] - 2026-02-27
### Added
- `direct` mode: no planning pass, raw prompt to model.
- `lite` mode (now default): one-pass inline `[P]/[A]` protocol and extraction.
- Preset profiles: `fast`, `balanced`, `strict` — control routing shape and token budgets.
- Lane policy: `default` and `strict_safe` — strict-format prompts route to direct path automatically.
- Local eval UI server (`quickthink ui`): single-page eval console at `http://127.0.0.1:7860`.
- Canonical eval harness: `run_suite.py`, `judge_suite.py`, `validate_judged_results.py`, `report_suite.py`, `make_gate_decision.py`.
- One-command quickstart script: `scripts/demo/quickstart.sh`.
- Release process and release-notes generator.

### Changed
- CLI gains `--mode`, `--preset`, `--lane-policy`, `--continuity-hint` options on `ask` and `bench`.
- New commands: `list-presets`, `compatibility`, `ui`.
- `two_pass` mode is now explicitly named (previously the only scaffold path).

### Fixed
- Python 3.9 compatibility for dataclass usage.
- `test_make_gate_decision`: replaced hardcoded `.venv/bin/python` with `sys.executable`.
