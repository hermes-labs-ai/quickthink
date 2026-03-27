# Troubleshooting

## Ollama is not reachable

Symptom:
- Connection refused or timeout errors.

Checks:

```bash
curl -fsS http://localhost:11434/api/tags
```

Fix:

```bash
ollama serve
```

## Model not found

Symptom:
- Unknown model or missing model errors.

Fix:

```bash
ollama pull qwen2.5:1.5b
ollama list
```

## `quickthink` command not found

Symptom:
- Shell cannot find `quickthink`.

Fix:

```bash
source .venv/bin/activate
pip install -e '.[dev]'
```

## UI does not load on 7860

Symptom:
- Browser page fails to load.

Fix:
1. Check for a port conflict on `7860`.
2. Stop the conflicting process.
3. Run `quickthink ui` again.

## Eval validation failures

Symptom:
- Run ingestion or report pipeline fails validation.

Fix:
1. Validate prompt set:
   - `python3 scripts/evals/validate_prompt_set.py --path docs/evals/prompt_set.jsonl`
2. Validate run file:
   - `python3 scripts/evals/validate_results.py --path <results.jsonl> --expected-prompts <n> --expected-runs <r> --models qwen2.5:1.5b mistral:7b gemma3:27b`
3. Validate judged file:
   - `python3 scripts/eval_harness/validate_judged_results.py --path <judged.jsonl>`
