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

Ask with compressed planning:

```bash
quickthink ask "How would a cow round up a border collie?" --model qwen2.5:1.5b
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

Launch local web UI (for eval/scaffolding testing):

```bash
quickthink ui
```

Then open `http://127.0.0.1:7860` if it does not open automatically.

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
