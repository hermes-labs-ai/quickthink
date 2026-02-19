# Public Repo Scope

This repository is the publishable runtime/evaluation surface for QuickThink/LittleBoost.

Included:
- runtime source code (`src/quickthink`)
- reusable evaluation harness (`scripts/eval_harness`, `docs/evals` prompt/spec files)
- tests and release process notes

Excluded from public tracking:
- internal multi-agent comms logs
- generated eval result dumps and ad-hoc local traces
- private experiment workspaces under `experiments-local/`

Branching policy:
- snapshot branches are frozen baselines
- cleanup and future work occur in separate branches
