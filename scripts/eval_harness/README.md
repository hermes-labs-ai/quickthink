# Eval Harness Scripts

Isolated A/B/C tooling that avoids core runtime/CLI edits.

## Scripts
- `run_suite.py`: executes full prompt set across modes/models and writes JSONL + manifest.
- `judge_suite.py`: scores run outputs (`rule` backend by default, optional `ollama` backend).
- `validate_judged_results.py`: strict schema validation for judged JSONL output.
- `report_suite.py`: builds model summary and pairwise win-rate reports.
- `run_variant_gate.py`: evaluates `direct` vs custom scaffold variants (e.g., Pipeline 1 winners), includes paired win rates, sign-test p-values, and lift-case extraction.

## Quickstart

```bash
./.venv/bin/python scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --out docs/evals/results/run_results.jsonl \
  --manifest-out docs/evals/results/run_manifest.json \
  --runs 3
```

```bash
./.venv/bin/python scripts/eval_harness/judge_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --results docs/evals/results/run_results.jsonl \
  --out docs/evals/results/judged_results.jsonl \
  --backend rule
```

```bash
./.venv/bin/python scripts/eval_harness/report_suite.py \
  --runs docs/evals/results/run_results.jsonl \
  --judged docs/evals/results/judged_results.jsonl \
  --out-json docs/evals/results/report_summary.json \
  --out-md docs/evals/results/report_summary.md
```

```bash
./.venv/bin/python scripts/eval_harness/validate_judged_results.py \
  --path docs/evals/results/judged_results.jsonl
```

## Optional Smoke Test

```bash
./.venv/bin/python scripts/eval_harness/run_suite.py --limit 3 --runs 1 --models qwen2.5:1.5b
```

## Variant Gate (Pipeline Winners)

```bash
./.venv/bin/python scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/evals/prompt_set_edge_cases.jsonl \
  --models qwen2.5:1.5b llama3.2:latest \
  --runs 2 \
  --top-k-variants 2 \
  --out-dir docs/evals/results/variant_gate_edge
```
