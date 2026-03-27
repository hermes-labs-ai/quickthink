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
	@if [ -z "$(VERSION)" ]; then echo "Usage: make release-check VERSION=x.y.z"; exit 1; fi
	PYTHONPATH=src .venv/bin/pytest -q
	python3 -m compileall -q src scripts tests
	python3 scripts/release/create_release_notes.py --version "$(VERSION)"
	@echo "Release check complete for v$(VERSION)."

attestation-verify:
	@if [ -z "$(REPO)" ] || [ -z "$(ARTIFACT)" ] || [ -z "$(SHA)" ]; then \
		echo "Usage: make attestation-verify REPO=owner/repo ARTIFACT=<name> SHA=<digest>"; \
		exit 1; \
	fi
	gh attestation verify --repo "$(REPO)" --artifact "$(ARTIFACT)" --sha256 "$(SHA)"
