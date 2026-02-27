# quickthink

`quickthink` is a lightweight scaffolding layer for local LLMs with two modes:
- `lite` (default): one-pass inline plan prefix + answer in a single generation
- `two_pass`: separate plan call then answer call

The plan can be logged as metadata while hidden from normal UI output.

## What this is / what this is not

What this is:
- A local middleware layer for Ollama-backed LLM calls.
- A small CLI for planned-answer generation, routing diagnostics, and local benchmarking.
- A canonical eval harness for reproducible project-level quality checks.

What this is not:
- Not a hosted API service.
- Not a model training framework.
- Not a replacement for full agent orchestration platforms.

## Why

Small/local models are fast but often underperform on multi-step tasks.
`quickthink` adds a strict planning pass (6-16 keyword tokens by default) to improve response quality without full verbose reasoning traces.

## MVP scope

- Ollama-first integration
- Model profiles:
  - `qwen2.5:1.5b`
  - `mistral:7b`
  - `gemma3:27b`
- Hidden plan by default, optional plan display/logging
- Bypass mode for short prompts (latency control)
- Adaptive routing (`skip`, `12-token`, `max-token` planning lanes)
- Strict plan grammar: `g:<...>;c:<...>;s:<...>;r:<...>`
- Hidden-plan extraction from inline output protocol:
  - `[P]g:...;c:...;s:...;r:...`
  - `[A]final answer`

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## 5-Minute Quickstart

Prerequisite: install and start [Ollama](https://ollama.com/) locally.

```bash
# 1) Clone and enter repo
git clone https://github.com/roli-lpci/quickthink.git quickthink  # or your fork URL
cd quickthink

# 2) Create env and install
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# 3) Pull one supported model
ollama pull qwen2.5:1.5b

# 4) Run your first command
quickthink ask "Give me a 3-step plan to learn SQL basics" --model qwen2.5:1.5b
```

If this command works, your local setup is ready.

## Documentation Map

- Docs index: `docs/README.md`
- First-time setup: `docs/GETTING_STARTED.md`
- Common failures and fixes: `docs/TROUBLESHOOTING.md`
- Known limitations: `docs/KNOWN_LIMITATIONS.md`
- Quick demo script: `docs/demo/QUICK_DEMO.md`
- OSS readiness scorecard: `docs/release/OSS_READINESS_SCORECARD_2026-02-25.md`
- OSS standards alignment (with external references): `docs/release/OSS_STANDARDS_ALIGNMENT_2026.md`
- Agent operating notes: `AGENTS.md`
- Owner notebook + GTM plan: `docs/research/QUICKTHINK_OWNER_NOTEBOOK_AND_GTM_2026-02-26.md`
- Strategy book (market/GTM positioning): `docs/research/QUICKTHINK_DELOITTE_STYLE_STRATEGY_BOOK_2026-02-26.md`
- Executive report: `docs/research/QUICKTHINK_PRODUCT_INITIATIVE_EXECUTIVE_REPORT_2026-02-26.md`

## Repository Layout

```text
src/quickthink/         Runtime package (CLI, engine, prompts, routing, UI server)
scripts/eval_harness/   Canonical evaluation pipeline (run/judge/validate/report)
scripts/evals/          Legacy smoke/demo helpers (non-canonical)
scripts/demo/           One-command local demo runner
docs/evals/             Prompt sets, rubrics, harness specs, deployment gate notes
docs/release/           Release process and repository audit notes
tests/                  Unit tests for runtime and harness safety checks
```

See full architecture + publishability audit:
`docs/release/REPO_STRUCTURE_AND_PUBLISHABILITY_AUDIT_2026-02-20.md`.

## Canonical vs Legacy Scripts

Canonical project workflows:
- `scripts/eval_harness/*`: maintained evaluation pipeline for run/judge/validate/report.
- `scripts/demo/quickstart.sh`: canonical end-to-end local smoke/demo flow.

Legacy helpers (kept for compatibility and ad-hoc smoke checks):
- `scripts/evals/*`: non-canonical helpers; do not treat as release gate source of truth.

When in doubt, use `scripts/eval_harness/*` and `scripts/demo/quickstart.sh`.

## Usage

List supported profiles:

```bash
quickthink list-models
```

List preset routing profiles:

```bash
quickthink list-presets
```

Show officially supported compatibility models:

```bash
quickthink compatibility
```

Ask with compressed planning:

```bash
quickthink ask "How would a cow round up a border collie?" --model qwen2.5:1.5b --preset balanced
```

Show plan in terminal:

```bash
quickthink ask "How would a cow round up a border collie?" --model mistral:7b --show-plan
```

Switch to two-pass mode:

```bash
quickthink ask "How would a cow round up a border collie?" --mode two_pass --show-route --show-plan
```

Show routing diagnostics:

```bash
quickthink ask "Design a robust parser with tradeoffs and a JSON output schema" --show-route --show-plan
```

Optional continuity hint (tiny, off by default):

```bash
quickthink ask "Continue the previous structure" --continuity-hint "ctx:prior_goal,format_json"
```

Strict-format-safe lane policy (routes strict format tasks to direct path first):

```bash
quickthink ask "json only: {\"ok\":true,\"why\":\"short\"}" --lane-policy strict_safe --show-route
```

Benchmark with strict-safe lane policy:

```bash
quickthink bench "Answer with YES or NO only: Is 2+2=4?" --lane-policy strict_safe --runs 3
```

Log plan + metrics as JSONL metadata:

```bash
quickthink ask "Design a tiny retry strategy" --log-file ./logs/quickthink.jsonl
```

Benchmark all three modes (lite, two_pass, direct):

```bash
quickthink bench "Design a robust parser for CSV with malformed quotes" --model qwen2.5:1.5b --runs 3
```

## One-Command Quickstart Demo

Run full local demo setup and artifact generation:

```bash
bash scripts/demo/quickstart.sh
```

It does:
- Python env + package install
- `ollama pull` for supported models
- Sample A/B/C eval run
- Result validation
- Markdown/HTML report generation
- Compatibility snapshot update

For a one-minute terminal walkthrough command set, see `docs/demo/QUICK_DEMO.md`.

Optional environment flags:
- `QUICKTHINK_PRESET=fast|balanced|strict`
- `QUICKTHINK_LIMIT=<n>` (number of prompts from canonical set)
- `QUICKTHINK_RUNS=<n>`
- `QUICKTHINK_RUN_JUDGE=1` (switch judge backend from `rule` to `ollama`)
- `QUICKTHINK_JUDGE_MODEL=<model>`

## Troubleshooting

For common setup/runtime failures and fixes, see `docs/TROUBLESHOOTING.md`.

## Reports

Canonical report flow:

```bash
python3 scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --out docs/evals/results/run-<timestamp>.jsonl \
  --manifest-out docs/evals/results/manifest-<timestamp>.json \
  --runs 3

python3 scripts/eval_harness/judge_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --results docs/evals/results/run-<timestamp>.jsonl \
  --out docs/evals/results/judged-<timestamp>.jsonl \
  --backend rule

python3 scripts/eval_harness/validate_judged_results.py \
  --path docs/evals/results/judged-<timestamp>.jsonl

python3 scripts/eval_harness/report_suite.py \
  --runs docs/evals/results/run-<timestamp>.jsonl \
  --judged docs/evals/results/judged-<timestamp>.jsonl \
  --out-json docs/evals/results/report-<timestamp>.json \
  --out-md docs/evals/results/report-<timestamp>.md \
  --out-html docs/evals/results/report-<timestamp>.html
```

Legacy helpers in `scripts/evals/*` remain available for smoke/demo use only.

## Compatibility Matrix

- Supported models are fixed to:
  - `qwen2.5:1.5b`
  - `mistral:7b`
  - `gemma3:27b`
- Experimental evaluations may include additional models (for example `llama3.2:latest`) in
  deployment-gate or variant-gate workflows. Treat those as research lanes unless promoted
  into `SUPPORTED_MODELS` in runtime config.
- Regenerate matrix + snapshot with:

```bash
python3 scripts/evals/compat_matrix_snapshot.py
```

Launch local web UI (for eval/scaffolding testing):

```bash
quickthink ui
```

Then open `http://127.0.0.1:7860` if it does not open automatically.

UI lane control:
- `Lane policy` dropdown supports `default` and `strict_safe` for single-prompt runs and 3-mode comparisons.

UI eval safety gates:
- Preflight is required before any eval run (`validate_prompt_set.py` must return `status=OK`).
- Run-file ingestion is blocked unless `validate_results.py` returns `status=OK`.
- UI displays validator output and dataset SHA256 for reproducible/comparable runs.

## Latency goals

- p50 overhead target: <80ms
- p95 overhead target: <200ms

Tune by reducing plan budgets and enabling prompt bypass.

## Productization path

Free/Open source:
- Local middleware + SDK + CLI

Paid:
- Hosted eval dashboards
- Team policy/profile management
- Managed observability and support

## Public Repo Scope

Included in this public repository:
- runtime source code (`src/quickthink`)
- reusable evaluation harness (`scripts/eval_harness`, `docs/evals` prompt/spec files)
- tests and release process notes

Excluded from public tracking:
- internal multi-agent comms logs
- generated eval result dumps and ad-hoc local traces
- private experiment workspaces under `experiments-local/`

## Branching

- Keep version tracks isolated in `codex/*` branches.
- Merge to `main` only after benchmarks and notes are updated.
- See `docs/VERSION_NOTES.md` for version-to-version differences.

## Maintainer Commands

Install (editable + dev):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Test:
```bash
PYTHONPATH=src .venv/bin/pytest -q
```

Lint (basic syntax/import sanity):
```bash
python -m compileall src tests scripts
```

Release docs + checklist:
```bash
make release-check VERSION=x.y.z
```
Follow:
- `docs/release/RELEASE_CHECKLIST.md`
- `docs/release/RELEASE_PROCESS.md`
- `docs/release/SUPPLY_CHAIN_BASELINE_2026.md`

## Caveats

- This does not guarantee better answers for every prompt.
- Gains are model/task dependent; run evals before claiming improvements.
- Hidden planning should remain auditable in logs for transparency.

## License

Apache-2.0
