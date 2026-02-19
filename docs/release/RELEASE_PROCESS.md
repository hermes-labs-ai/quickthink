# Release Process

This project uses semantic versioning.

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
2. Generate compatibility matrix snapshot:
   - `python3 scripts/evals/compat_matrix_snapshot.py`
3. Generate release notes draft:
   - `python3 scripts/release/create_release_notes.py --version <x.y.z>`
4. Update `pyproject.toml` version.
5. Commit with message: `release: v<x.y.z>`.
6. Tag and push:
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
