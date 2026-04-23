# AGENTS.md

`quickthink` is a local-first inference control layer that adds a compressed planning scaffold
to small LLMs, with latency-aware routing and an eval harness for reproducible quality checks.

## Use it for

- adding a structured planning scaffold to Ollama-backed LLM calls
- routing between lite/two-pass/direct modes based on prompt complexity
- running a canonical eval harness (run/judge/validate/report) for quality gating
- benchmarking small-model output reliability across preset profiles

## Do not use it for

- hosted API calls (local-first only)
- full agent orchestration
- guaranteeing performance improvements (gains are model/task dependent)

## Minimal commands

```bash
pip install -e ".[dev]"
quickthink --help
quickthink ask "Design a retry strategy" --model qwen2.5:1.5b
pytest -q
ruff check src/ tests/
```

## Repository layout

```
src/quickthink/         Runtime package (CLI, engine, prompts, routing, UI server)
scripts/eval_harness/   Canonical evaluation pipeline (run/judge/validate/report)
tests/                  Unit tests for runtime and harness safety checks
docs/                   Documentation, eval specs, release process
```

## Output shape

- CLI: structured text answer (plan hidden by default; `--show-plan` to reveal)
- `--log-file`: JSONL metadata per call (plan, route, latency, tokens)
- `quickthink ui`: single-page eval console at http://127.0.0.1:7860
- Harness: JSON/Markdown/HTML reports from the run/judge/validate/report pipeline

## Success means

- `quickthink ask` returns a coherent answer with no scaffold artifacts in output
- tests pass: `PYTHONPATH=src pytest -q`
- same prompt/mode/model produces consistent routing and plan structure across runs

## Common failure cases

- Ollama not running locally — start with `ollama serve`
- Model not pulled — `ollama pull qwen2.5:1.5b`
- Structured-format prompts route to direct path automatically under `strict_safe` lane policy

## Guardrails

- Do not change eval scoring semantics or runtime model behavior for cleanup-only work
- `scripts/eval_harness/*` is the canonical pipeline; `scripts/evals/*` are legacy helpers
- Keep user-facing claims bounded; avoid universal or guaranteed-performance language
- Preserve pinned GitHub Actions SHAs when editing workflow files

## Maintainer notes

- Supported models are pinned in runtime config; experimental models go in research lanes only
- CHANGELOG must have an entry for any version change before release
- Release checklist: `docs/release/RELEASE_CHECKLIST.md`
