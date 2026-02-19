# Contributing to quickthink

Thanks for contributing to `quickthink`.

## Before you start
- Use Python 3.9+.
- Create and activate a virtual environment.
- Install dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Development workflow
1. Create a branch from `main` using the `codex/` prefix.
2. Make focused changes with clear commit messages.
3. Run tests before opening a PR:

```bash
PYTHONPATH=src .venv/bin/pytest -q
```

4. Update docs if user-facing behavior or workflows changed.

## Pull request expectations
- Keep PRs small and reviewable.
- Include the problem, approach, and validation steps.
- Link related issues (if any).
- Confirm tests pass locally.

## Scope notes
- Runtime code is in `src/quickthink/`.
- Canonical eval pipeline is `scripts/eval_harness/`.
- `scripts/evals/` contains legacy smoke/demo helpers.
- `experiments-local/` is private/local workspace material and not part of public maintenance workflows.

## Code style
- Prefer clear, minimal solutions.
- Keep docs and examples copy-paste ready.
- Avoid unrelated refactors in the same PR.
