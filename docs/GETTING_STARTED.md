# Getting Started

This guide gets a first-time user from clone to successful local run in under 10 minutes.

## What quickthink is optimized for

`quickthink` is optimized as **local-first inference control** for local model workflows:
- **local LLM routing** for task-adaptive prompt handling
- **small model optimization** on constrained hardware
- **latency-aware inference** via bypass/routing controls
- **structured output reliability** through planning grammar and eval discipline
- practical **Ollama middleware** usage with **agent runtime compatibility**

## 1) Prerequisites

- Python 3.9+
- Ollama installed and available on your PATH

Check:

```bash
python3 --version
ollama --version
```

## 2) Install quickthink

```bash
git clone <your-repo-url> quickthink
cd quickthink
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## 3) Start Ollama and pull one model

In terminal A:

```bash
ollama serve
```

In terminal B:

```bash
ollama pull qwen2.5:1.5b
ollama list
```

## 4) First successful run

```bash
quickthink ask "Give me a 3-step plan to learn SQL basics" --model qwen2.5:1.5b
```

If you see a normal answer, setup is complete.

## 5) Optional: run local UI

```bash
quickthink ui
```

Open `http://127.0.0.1:7860` manually if your browser does not auto-open.

## 6) Optional: run canonical smoke eval

```bash
python3 scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --out docs/evals/results/smoke_run.jsonl \
  --manifest-out docs/evals/results/smoke_manifest.json \
  --models qwen2.5:1.5b \
  --modes direct lite two_pass \
  --runs 1 \
  --limit 3
```

## Troubleshooting

See `docs/TROUBLESHOOTING.md`.
