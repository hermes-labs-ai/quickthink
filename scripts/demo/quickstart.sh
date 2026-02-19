#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
PRESET="${QUICKTHINK_PRESET:-balanced}"
LIMIT="${QUICKTHINK_LIMIT:-4}"
RUNS="${QUICKTHINK_RUNS:-1}"
RUN_JUDGE="${QUICKTHINK_RUN_JUDGE:-0}"
JUDGE_MODEL="${QUICKTHINK_JUDGE_MODEL:-gemma3:27b}"

TS="$(date -u +%Y%m%d-%H%M%S)"
RESULTS_FILE="docs/evals/results/run-${TS}.jsonl"
MANIFEST_FILE="docs/evals/results/manifest-${TS}.json"
JUDGED_FILE="docs/evals/results/judged-${TS}.jsonl"
REPORT_JSON="docs/evals/results/report-${TS}.json"
REPORT_MD="docs/evals/results/report-${TS}.md"
REPORT_HTML="docs/evals/results/report-${TS}.html"

echo "[1/8] Creating/updating virtualenv"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -e '.[dev]' >/dev/null

echo "[2/8] Checking Ollama"
if ! command -v ollama >/dev/null 2>&1; then
  echo "error: ollama not found. Install first: brew install ollama"
  exit 1
fi

if ! curl -fsS "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  echo "error: Ollama is not reachable at ${OLLAMA_URL}. Start it with: ollama serve"
  exit 1
fi

echo "[3/8] Pulling supported models (qwen2.5:1.5b, mistral:7b, gemma3:27b)"
ollama pull qwen2.5:1.5b
ollama pull mistral:7b
ollama pull gemma3:27b

echo "[4/8] Validating eval dataset"
python3 scripts/evals/validate_prompt_set.py --path docs/evals/prompt_set.jsonl

echo "[5/8] Running canonical eval harness (A/B/C modes)"
python3 scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --out "$RESULTS_FILE" \
  --manifest-out "$MANIFEST_FILE" \
  --ollama-url "$OLLAMA_URL" \
  --limit "$LIMIT" \
  --runs "$RUNS" \
  --models qwen2.5:1.5b mistral:7b gemma3:27b

echo "[6/8] Validating sample results"
python3 scripts/evals/validate_results.py \
  --path "$RESULTS_FILE" \
  --expected-prompts "$LIMIT" \
  --expected-runs "$RUNS" \
  --models qwen2.5:1.5b mistral:7b gemma3:27b

echo "[7/8] Building shareable report"
JUDGE_BACKEND="rule"
if [[ "$RUN_JUDGE" == "1" ]]; then
  JUDGE_BACKEND="ollama"
fi
echo "Running judge backend: $JUDGE_BACKEND"
python3 scripts/eval_harness/judge_suite.py \
    --prompt-set docs/evals/prompt_set.jsonl \
    --results "$RESULTS_FILE" \
    --out "$JUDGED_FILE" \
    --backend "$JUDGE_BACKEND" \
    --judge-model "$JUDGE_MODEL" \
    --ollama-url "$OLLAMA_URL"
python3 scripts/eval_harness/validate_judged_results.py --path "$JUDGED_FILE"
python3 scripts/eval_harness/report_suite.py \
  --runs "$RESULTS_FILE" \
  --judged "$JUDGED_FILE" \
  --out-json "$REPORT_JSON" \
  --out-md "$REPORT_MD" \
  --out-html "$REPORT_HTML"

echo "[8/8] Generating compatibility snapshot"
python3 scripts/evals/compat_matrix_snapshot.py --ollama-url "$OLLAMA_URL" --preset "$PRESET"

echo "Done."
echo "- Results: $RESULTS_FILE"
echo "- Manifest: $MANIFEST_FILE"
echo "- Judged:  $JUDGED_FILE"
echo "- Report:  $REPORT_MD"
echo "- HTML:    $REPORT_HTML"
if command -v open >/dev/null 2>&1; then
  open "$REPORT_HTML" || true
fi
