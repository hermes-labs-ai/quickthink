# Changelog

All notable changes to this project should be documented in this file.

Format follows Keep a Changelog principles and semantic versioning.

## [Unreleased]

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
