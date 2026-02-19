# Release Checklist

Use this checklist for every public release.

## 1) Tests pass
Run:

```bash
PYTHONPATH=src .venv/bin/pytest -q
```

Expected: all tests passing, no regressions.

## 2) Quickstart smoke
Run:

```bash
bash scripts/demo/quickstart.sh
```

Expected:
- Demo completes without fatal errors.
- Eval/report artifacts are generated.

## 3) Changelog update
Update `CHANGELOG.md` with:
- version heading (`x.y.z`)
- date
- notable user-facing changes
- any migration notes

## 4) Version bump
Update the package version in `pyproject.toml`:
- `[project].version = "x.y.z"`

## 5) Tag + release notes
Generate draft notes:

```bash
python3 scripts/release/create_release_notes.py --version <x.y.z>
```

Then:

```bash
git add -A
git commit -m "release: v<x.y.z>"
git tag v<x.y.z>
git push origin <branch>
git push origin v<x.y.z>
```

Create a GitHub Release for tag `v<x.y.z>` and paste finalized release notes.

## Optional packaging validation
Before publishing to package indexes, run:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```
