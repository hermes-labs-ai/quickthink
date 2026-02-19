# Roundtable Summary (Lead)

Date: 2026-02-18
Lead: codex-core
Participants (from comms log): codex-core, codex-eval-harness, codex-hardening

## 1) State of the Goal
Goal remains intact and achievable:
- Deliver a deployable local-first LPCI-lite scaffold with measurable quality/latency gains.
- Keep product shape simple: one-pass `lite` as default, two-pass available for controlled comparisons.

Current maturity:
- Core runtime exists and is test-backed.
- Eval infrastructure exists (two tracks: `scripts/evals` and `scripts/eval_harness`).
- Hardening work landed for safety and judged-output validation.

## 2) State of the Code
Healthy but converging:
- Tests are passing (`19 passed`).
- Presets, quickstart automation, report generation, compatibility snapshots, and release docs are in place.
- UI safety hardening has been added.

Main risk now:
- Duplicate eval pipelines (`scripts/evals` vs `scripts/eval_harness`) may create confusion.

## 3) Achievability / Viability Rating (current)
- Achievability (ship functional OSS in near-term): 8.8/10
- Technical viability (sustained, reproducible value): 7.9/10
- Adoption readiness (non-technical onboarding): 7.5/10

Why not higher yet:
- Need one canonical eval pipeline and a single source of truth for published benchmark claims.

## 4) Decisions Recommended (conservative)
1. Declare one eval path canonical (recommend `scripts/eval_harness` for stricter safety) and keep the other as legacy until removed.
2. Require artifact-backed claims only (report + compatibility snapshot + judged validation).
3. Keep supported-model list fixed for now (`qwen2.5:1.5b`, `mistral:7b`, `gemma3:27b`).
4. Keep `lite` default and avoid adding new modes until public feedback arrives.

## 5) Advice to Product Owner (you)
Strengths:
- You set strong product constraints (simplicity, speed, practical utility) and prevent scope drift.
- You naturally push toward real user value over architecture vanity.

Watchouts:
- Parallel agents can silently create duplicate systems unless you force a canonical path early.
- Fast iteration is good; freeze points are equally important.

Operating pattern to maximize your leverage:
- Work in short cycles with explicit stage gates:
  - Gate A: functionality
  - Gate B: metrics
  - Gate C: docs/reproducibility
- Ask every agent for: "What did you add, what did you remove, what do we deprecate now?"

## 6) Lead Closeout
Roundtable complete.
Lead recommendation: move immediately to pipeline consolidation + one publishable benchmark pack.
