---
name: quickthink
description: Use when routing a prompt through a local Ollama model needs a compressed plan-then-answer scaffold for multi-step prompts and a direct pass-through for simple ones — quickthink wraps the model call with latency-aware routing across three modes (lite/two_pass/direct). Local-first, no MCP.
license: Apache-2.0
compatibility: Requires Python 3.9+; installs via pip. Requires a running local Ollama instance with a supported model pulled (qwen2.5:1.5b, mistral:7b, or gemma3:27b).
---

# quickthink

quickthink is a local-first CLI and Python library that wraps Ollama-backed
LLM calls with a compressed plan-then-answer scaffold and latency-aware
routing. It adds a short, validated planning step for prompts that look
multi-step, and routes simple prompts straight through to the model.

## Use it for

- Improving small/local model quality on multi-step prompts with a strict,
  bounded planning pass (6-16 keyword tokens by default)
- Comparing routing/latency behavior across `lite` (default), `two_pass`, and
  `direct` modes for the same prompt
- Benchmarking a prompt across all three modes to see which is fastest for a
  given task shape
- Inspecting the exact routing decision and prompt(s) without calling Ollama
  (`--dry-run`)

## Do not use it for

- A hosted API service, a model training framework, or a full agent
  orchestration platform
- Any model outside the three pinned, tuned profiles (`qwen2.5:1.5b`,
  `mistral:7b`, `gemma3:27b`) without expecting untuned behavior
- Guaranteeing correctness — when the generated plan fails its grammar check,
  the engine substitutes a fixed fallback plan; this keeps the format valid,
  not the answer correct

## Quickstart

```bash
python -m pip install "quickthink==0.2.2"
ollama pull qwen2.5:1.5b
quickthink ask "Give me a 3-step plan to learn SQL basics" --model qwen2.5:1.5b
```

Show the plan and routing diagnostics:

```bash
quickthink ask "How would a cow round up a border collie?" --mode two_pass --show-route --show-plan
```

Skip planning entirely:

```bash
quickthink ask "What is the capital of France?" --mode direct
```

Benchmark all three modes:

```bash
quickthink bench "Design a robust parser for CSV with malformed quotes" --model qwen2.5:1.5b --runs 3
```

## Output shape

- `quickthink ask`: prints the model's answer; `--show-plan` reveals the
  hidden planning pass, `--show-route` reveals the routing decision
- `quickthink list-models` / `quickthink list-presets` / `quickthink
  compatibility`: list supported models, routing presets, and officially
  supported compatibility models
- `--log-file path.jsonl`: appends plan and metrics metadata as JSONL

## Common gotchas

- Two-pass mode makes one extra model call versus direct mode — the planning
  step is real latency and cost, not free.
- Only three pinned models are tuned; other Ollama models may run but their
  behavior with the planning scaffold is untuned.
- Whether the planning scaffold actually helps is model- and task-dependent
  — run the eval harness (`scripts/eval_harness/*`) rather than assuming it.
- This is a local CLI/library, not an MCP server; it talks only to a local
  Ollama HTTP endpoint.

## More

Full docs and CLI reference:
https://github.com/hermes-labs-ai/quickthink
