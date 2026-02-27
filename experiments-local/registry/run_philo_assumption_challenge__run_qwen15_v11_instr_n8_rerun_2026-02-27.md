# Run Trace: philo_assumption_challenge/run_qwen15_v11_instr_n8_rerun_2026-02-27

## Identity
- track: `philo_assumption_challenge`
- run_id: `run_qwen15_v11_instr_n8_rerun_2026-02-27`
- status: `active`
- owner/session: Codex throttled completion rerun after prior stalled attempt

## Configuration
- models: `qwen2.5:1.5b`
- runs_per_prompt: `8`
- prompt_set: `docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl`
- variants_file: `experiments-local/philo_assumption_challenge_2026-02-25/phenomenology_variant_qwen_v11_only.json`
- variants: `v11_instruction_validator`
- mode/preset: `lite` / `balanced`
- throttle: `--cooldown-every-calls 6 --cooldown-seconds 300`

## Commands
```bash
PYTHONPATH=src python3 scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/research/codex/experiments/prompt_subset_balanced12_2026-02-25.jsonl \
  --out-dir experiments-local/philo_assumption_challenge_2026-02-25/run_qwen15_v11_instr_n8_rerun_2026-02-27 \
  --variants-file experiments-local/philo_assumption_challenge_2026-02-25/phenomenology_variant_qwen_v11_only.json \
  --top-k-variants 1 --models qwen2.5:1.5b --runs 8 --mode lite --preset balanced --request-timeout-s 180 \
  --resume --cooldown-every-calls 6 --cooldown-seconds 300
```

## Artifacts
- run_dir: `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen15_v11_instr_n8_rerun_2026-02-27/`
- meta: `.../meta.json`
- run_results: `.../run_results.jsonl`
- judged_results: `.../judged_results.jsonl`
- summary_md: `.../summary.md`
- summary_json: `.../summary.json`
- lift_cases: `.../lift_cases.jsonl`
- extras: `.../checkpoint.json`

## Snapshot
- avg score delta vs direct: `v11 -0.031` (direct `5.656`, variant `5.625`)
- pairwise vs direct: `wins=21 losses=22 ties=53`, `non_tie_win_rate=0.488`, `pvalue=1.0`
- latency delta: `+8.44 ms` (slower than direct)
- warning: `structured_output` regression (`-0.542`)

## Decision role
- why this run matters:
  - completes previously stalled qwen v11 confirmation at target sample size with machine-safe throttling.
  - falsifies earlier optimistic small-n direction for qwen instruction-lane v11.
- superseded by (if any):
  - pending future tuned qwen instruction-lane variants
