#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
cat <<'TXT'
Agent bootstrap reading order:
1) AGENTS.md
2) FOLDER_MAP.md
3) docs/MARKDOWN_INDEX.md
4) docs/research/R_AND_D_LEDGER.md
5) experiments-local/registry/INDEX.md
TXT
