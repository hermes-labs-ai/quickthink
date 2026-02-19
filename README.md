# quickthink

`quickthink` is a lightweight scaffolding layer for local LLMs with two modes:
- `lite` (default): one-pass inline plan prefix + answer in a single generation
- `two_pass`: separate plan call then answer call

The plan can be logged as metadata while hidden from normal UI output.

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

Optional environment flags:
- `QUICKTHINK_PRESET=fast|balanced|strict`
- `QUICKTHINK_LIMIT=<n>` (number of prompts from canonical set)
- `QUICKTHINK_RUNS=<n>`
- `QUICKTHINK_RUN_JUDGE=1` (switch judge backend from `rule` to `ollama`)
- `QUICKTHINK_JUDGE_MODEL=<model>`

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
- Regenerate matrix + snapshot with:

```bash
python3 scripts/evals/compat_matrix_snapshot.py
```

Launch local web UI (for eval/scaffolding testing):

```bash
quickthink ui
```

Then open `http://127.0.0.1:7860` if it does not open automatically.

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

## Caveats

- This does not guarantee better answers for every prompt.
- Gains are model/task dependent; run evals before claiming improvements.
- Hidden planning should remain auditable in logs for transparency.

## License

Apache-2.0
