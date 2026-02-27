#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0

req_files=(
  "docs/research/R_AND_D_LEDGER.md"
  "experiments-local/registry/INDEX.md"
  "experiments-local/operations/model_routing_policy_v1.json"
  "docs/research/MODEL_DEFAULTS_AND_GUARDRAILS_2026-02-26.md"
  "docs/SESSION_CLOSEOUT_CHECKLIST.md"
)

for f in "${req_files[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    fail=1
  fi
done

# Ensure every run trace referenced in registry index exists.
if [[ -f "experiments-local/registry/INDEX.md" ]]; then
  while IFS= read -r t; do
    [[ -z "$t" ]] && continue
    if [[ ! -f "$t" ]]; then
      echo "BROKEN_REGISTRY_REFERENCE: $t"
      fail=1
    fi
  done < <(rg -o 'experiments-local/registry/run_[^` ]+\.md' experiments-local/registry/INDEX.md | sort -u)
fi

# Ensure markdown index references the canonical ledger and registry.
if [[ -f "docs/MARKDOWN_INDEX.md" ]]; then
  rg -q "docs/research/R_AND_D_LEDGER.md" docs/MARKDOWN_INDEX.md || { echo "MISSING_INDEX_ENTRY: R_AND_D_LEDGER"; fail=1; }
  rg -q "experiments-local/registry/INDEX.md" docs/MARKDOWN_INDEX.md || { echo "MISSING_INDEX_ENTRY: REGISTRY_INDEX"; fail=1; }
fi

# Basic freshness hint: ensure ledger has at least one Entry in last 50 lines.
if [[ -f "docs/research/R_AND_D_LEDGER.md" ]]; then
  tail -n 50 docs/research/R_AND_D_LEDGER.md | rg -q "^### Entry" || { echo "LEDGER_STALE_HINT: no recent Entry heading in last 50 lines"; fail=1; }
fi

if [[ "$fail" -ne 0 ]]; then
  echo "research_hygiene_check=FAIL"
  exit 1
fi

echo "research_hygiene_check=PASS"
