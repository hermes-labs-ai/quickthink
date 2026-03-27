# Model Lane Strategy (2026-02-25)

## Purpose
Define a practical R&D path to test whether QuickThink can move from model-specific scaffold lanes to one or two shared scaffold families without losing quality/latency performance.

## Inputs
Internal inputs (repo-grounded):
- `experiments-local/model_champions.json`
- `experiments-local/model-scaffolds-and-decisions.md`
- `experiments-local/variant_matrix_all_models.md`
- `scripts/eval_harness/run_variant_gate.py`
- `scripts/eval_harness/run_frozen_experiment.py`
- `docs/evals/harness_spec.md`
- `docs/evals/failure_modes.md`

External inputs (usage proxies; captured 2026-02-25 UTC):
- Ollama Library popular models (pull counts): <https://ollama.com/library>
  - `llama3.2`: 150.6M pulls
  - `deepseek-r1`: 63.8M pulls
  - `qwen2.5`: 58.4M pulls
  - `gemma3`: 17.9M pulls
  - `mistral`: 17.6M pulls
- Hugging Face API download proxies (family-level signal):
  - <https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct>
  - <https://huggingface.co/api/models/meta-llama/Llama-3.2-3B-Instruct>
  - <https://huggingface.co/api/models/google/gemma-3-4b-it>
  - <https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.3>

## Outputs
Current state diagnosis:
- Yes: active winners are model-lane specific today.
- The fixed scaffold shape is already shared (`[P]g;c;s;r` + `[A]`), but inserted rule text differs by model lane.
- Common rule overlap already exists across lanes: "keep final answer concise unless task requests expansion" appears in both qwen and llama winners.

Recommended target model lanes (near-term):
1. `llama3.2` family (largest Ollama pull signal)
2. `qwen2.5/qwen3` family (strong Ollama + HF signal)
3. `deepseek-r1` family (strong Ollama pull signal; reasoning-heavy demand)

Recommended scaffold strategy (hybrid):
- Must: keep a model-lane override mechanism.
- Must: test shared scaffold families first before minting new per-model variants.
- May: keep per-model champions only when shared scaffold misses gate thresholds.

Proposed shared scaffold families to test first:
1. `concise_core`
- `keep final answer concise unless task requests expansion`

2. `concise_plus_shape`
- `keep final answer concise unless task requests expansion; prioritize exact requested output shape`

3. `concise_plus_logic`
- `keep final answer concise unless task requests expansion; verify numeric or logical consistency before answer`

Use-case wedges where QuickThink is most differentiated (from eval structure + failure modes):
1. Instruction-constrained outputs (strict formats, brevity, casing)
2. Structured output correctness (JSON/YAML/SQL/table forms)
3. Multi-turn continuity with explicit constraints

## Commands
Baseline frozen comparison across target lanes:
```bash
PYTHONPATH=src .venv/bin/python scripts/eval_harness/run_frozen_experiment.py \
  --name tri-lane-shared-scaffold-baseline \
  --models llama3.2:latest qwen2.5:1.5b deepseek-r1:latest \
  --per-group 8 \
  --runs 3
```

Variant gate with top shared scaffolds:
```bash
PYTHONPATH=src .venv/bin/python scripts/eval_harness/run_variant_gate.py \
  --models llama3.2:latest qwen2.5:1.5b deepseek-r1:latest \
  --top-k-variants 3 \
  --runs 3 \
  --preset balanced \
  --mode lite
```

Project validation commands:
```bash
PYTHONPATH=src .venv/bin/pytest -q
python3 -m compileall -q src scripts tests
```

## Limits
- Ollama pull counts are a popularity proxy, not active-user counts.
- HF download counts are a proxy and include non-local usage paths.
- Existing internal winner evidence is strong for qwen/llama but still small-N (`24` prompts, `2` repeats in frozen winner report).
- Compatibility snapshot in `docs/compatibility_matrix.md` is environment-scoped; do not generalize universally.

## Decision Gate (Proposed)
Promote a shared scaffold family only if all are true:
- Quality delta vs direct >= +0.20 on each target lane.
- No per-group regression <= -0.25 in reasoning/structured/multi-turn groups.
- p95 latency overhead <= 200ms vs direct (or better).
- Results are stable across >=2 reruns with same prompt subset.

If shared scaffold fails one lane:
- Keep shared scaffold as default.
- Keep lane-specific override only for the failing lane.

## Next R&D Sequence
1. Freeze candidate shared scaffold set (`concise_core`, `concise_plus_shape`, `concise_plus_logic`).
2. Run tri-lane variant gate with 3 repeats and balanced prompt mix.
3. Publish one summary table per model lane and one global recommendation table.
4. Decide default policy:
- Option A: one global scaffold + lane overrides
- Option B: two global scaffold families selected by task type
- Option C: keep lane-specific champions
