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

Recommended release publication order:
1. Create release as **draft**.
2. Attach release assets (notes, hashes, SBOM/attestation artifacts when available).
3. Final review.
4. Publish release (treat as immutable after publish).

## Optional packaging validation
Before publishing to package indexes, run:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

## 6) 2026 supply-chain baseline (recommended)
For public OSS releases, complete these before marking a release final:

1. Generate and publish build provenance attestation for release assets (or record why not yet enabled).
2. Generate and publish an SBOM (SPDX or CycloneDX) for the release assets.
3. Verify attestation in CI or locally (`gh attestation verify ...`) and retain proof in release notes.
4. Use immutable releases when available (publish as draft first, attach assets, then publish).
5. Ensure workflow token permissions are least-privilege and review third-party action pinning policy.

Reference baseline and rationale:
- `docs/release/SUPPLY_CHAIN_BASELINE_2026.md`
