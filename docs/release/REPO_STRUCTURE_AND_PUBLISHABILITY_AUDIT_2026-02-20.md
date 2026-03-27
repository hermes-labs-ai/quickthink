# Repository Structure And Publishability Audit (2026-02-20)

## Scope

This audit covers all tracked source, scripts, docs, and tests intended for GitHub publication.

Branch audited:
- `codex/cleanup-pass-2026-02-20`

Validation run:
- `PYTHONPATH=src .venv/bin/pytest -q` -> `19 passed`
- `python3 -m compileall -q src scripts tests` -> `OK`

---

## 1) Repository Architecture (What Exists)

### Runtime package (`src/quickthink`)

- `config.py`
  - Defines runtime model profiles, preset profiles, and the `QuickThinkConfig` dataclass.
  - Runtime support list is fixed in code (`SUPPORTED_MODELS`).
- `routing.py`
  - Prompt complexity scoring and bypass decision logic.
  - Chooses whether to run scaffold or direct path, and selects plan token budget.
- `prompts.py`
  - Prompt template builders for:
    - one-pass inline protocol (`[P]...` + `[A]...`)
    - two-pass plan generation
    - plan repair
- `plan_grammar.py`
  - Plan normalization/validation and token estimation for strict compact grammar.
- `inline_protocol.py`
  - Extracts internal plan and final answer from model output.
- `ollama_client.py`
  - HTTP client wrapper for `/api/generate`.
- `engine.py`
  - Core orchestrator (`QuickThinkEngine`) for:
    - `direct` behavior via bypass
    - `lite` mode (single generation, inline plan+answer)
    - `two_pass` mode (plan call, optional repair, answer call)
  - Emits standardized `QuickThinkResult` metrics fields.
- `cli.py`
  - User entrypoint (`quickthink` commands): `ask`, `bench`, `ui`, model/preset listing.
- `ui_server.py`
  - Local internal browser UI for eval/testing workflows.

### Evaluation scripts

- Canonical path: `scripts/eval_harness/*`
  - `run_suite.py` (runner + manifest)
  - `judge_suite.py` (rule/ollama judge)
  - `validate_judged_results.py` (schema gate)
  - `report_suite.py` (summary reports)
  - `run_variant_gate.py` (direct vs selected variants)
- Legacy path: `scripts/evals/*`
  - Kept intentionally as smoke/demo helpers.
  - Explicitly marked non-canonical.

### Docs

- `docs/evals/*`
  - Prompt sets, rubrics, harness spec, failure mode notes, deployment gate criteria.
- `docs/release/*`
  - Release process and cleanup/snapshot notes.
- `docs/compatibility_matrix.md`
  - Snapshot-style compatibility/latency table.

### Tests

- Runtime behavior tests (`routing`, `prompts`, `plan_grammar`, `inline_protocol`).
- Safety checks around eval harness and UI path constraints.

---

## 2) Publishability Audit (Findings)

Severity scale:
- `P1` blocking correctness/security issue
- `P2` high confusion/reputation risk for public users
- `P3` maintainability/readability issue

### Findings

1. `P2` Model policy is split across runtime and eval docs.
- Runtime support list is `qwen2.5:1.5b`, `mistral:7b`, `gemma3:27b`.
- Some deployment/eval docs use additional research lanes (for example `llama3.2:latest`).
- Risk: users misread experimental model lanes as officially supported runtime defaults.

2. `P2` Canonical vs legacy script split exists but can still be missed.
- Both `scripts/eval_harness/*` and `scripts/evals/*` are present.
- Current docs do clarify this, but public readers can still jump into legacy scripts first.

3. `P3` `ui_server.py` is monolithic and mixes large inline HTML/CSS with server logic.
- No immediate correctness issue.
- Readability and long-term maintainability cost are high.

4. `P3` Compatibility snapshot can look counterintuitive without environment context.
- Snapshot includes large negative overhead values in some rows.
- Without hardware + prompt-length context, public readers may misinterpret as universal claims.

### No blocking issues found

- No `P1` correctness failures surfaced in tests.
- Harness lock file safety and judged-result schema gates are present.
- Path-safety checks exist in UI ingestion helpers.

---

## 3) Changes Applied In This Pass

1. Added repository layout section to `README.md` for human scanability.
2. Added explicit model policy wording in `README.md`:
   - supported runtime models vs experimental eval lanes.
3. Added this full architecture + publishability audit document.

---

## 4) Recommended Next Cleanup Pass (Conservative)

1. Move inline HTML in `src/quickthink/ui_server.py` into a static template file.
2. Add a short `CONTRIBUTING.md` with:
   - canonical eval commands
   - branch policy
   - claim discipline for benchmark publication.
3. Add context footer to `docs/compatibility_matrix.md`:
   - machine specs
   - prompt set used
   - whether token caps were normalized.
4. Keep `experiments-local/` private and out of public release tags.

---

## 5) Human Summary

The repository is structurally coherent and publishable after current cleanup.

What it is now:
- a small runtime package
- a clear canonical evaluation harness
- a test suite that passes
- documented release process

What still needs polish (non-blocking):
- reduce UI server file size/complexity
- tighten public model-support messaging everywhere
- annotate benchmark snapshots with context to avoid overclaim interpretation
