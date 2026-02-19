install:
	python -m venv .venv
	.venv/bin/pip install -e '.[dev]'

test:
	PYTHONPATH=src .venv/bin/pytest -q

compile-check:
	python3 -m compileall -q src scripts tests

smoke-eval:
	python3 scripts/eval_harness/run_suite.py --prompt-set docs/evals/prompt_set.jsonl --out docs/evals/results/smoke_run.jsonl --manifest-out docs/evals/results/smoke_manifest.json --models qwen2.5:1.5b --modes direct lite two_pass --runs 1 --limit 3

release-check:
	@echo "Use docs/release/RELEASE_CHECKLIST.md and workflow release-check.yml"
