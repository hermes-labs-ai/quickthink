# Release Process

This project uses semantic versioning.

Primary operator checklist:
- `docs/release/RELEASE_CHECKLIST.md`
This checklist is the source-of-truth execution order for release day.

## Versioning Rules
- `MAJOR`: breaking API/behavior changes.
- `MINOR`: backward-compatible feature additions.
- `PATCH`: bug fixes and non-breaking improvements.

## Required Artifacts Before Release
1. Passing tests (`pytest`).
2. Eval report artifact (`docs/evals/results/report-*.md` + `.html`).
3. Compatibility snapshot (`docs/compatibility/snapshots/*.json`).
4. Release notes generated from artifacts.

## Release Steps
1. Run quickstart benchmark flow:
   - `bash scripts/demo/quickstart.sh`
2. Run tests:
   - `PYTHONPATH=src .venv/bin/pytest -q`
3. Generate compatibility matrix snapshot:
   - `python3 scripts/evals/compat_matrix_snapshot.py`
4. Generate release notes draft:
   - `python3 scripts/release/create_release_notes.py --version <x.y.z>`
5. Update `pyproject.toml` version.
6. Update `CHANGELOG.md`.
7. Commit with message: `release: v<x.y.z>`.
8. Tag and push:
   - `git tag v<x.y.z>`
   - `git push origin <branch> --tags`

## Packaging
Build/check package locally:
- `python -m pip install --upgrade build`
- `python -m build`

Optional publish (when ready):
- `python -m pip install --upgrade twine`
- `python -m twine check dist/*`
- `python -m twine upload dist/*`
