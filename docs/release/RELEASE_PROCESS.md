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
8. Merge the release commit only after its hosted checks pass.
9. For a PyPI release, configure the PyPI trusted publisher once with this exact tuple:
   - owner: `hermes-labs-ai`
   - repository: `quickthink`
   - workflow: `publish.yml`
   - environment: `pypi`
10. Tag and push the merged commit:
   - `git tag v<x.y.z>`
   - `git push origin v<x.y.z>`

The tag workflow checks that `v<x.y.z>` exactly matches `[project].version`, builds and
checks distributions in a separate job, then publishes the artifact through PyPI OIDC.
It uses no PyPI API token. The existing `v0.2.0` tag predates this workflow, so the first
PyPI release must use a new version and matching tag (for example, `v0.2.1`).

## Packaging
Build/check package locally:
- `python -m pip install --upgrade build`
- `python -m build`

Check the distributions locally:
- `python -m pip install --upgrade twine`
- `python -m twine check dist/*`

Do not run `twine upload`; publishing is performed only by the trusted-publisher workflow.
