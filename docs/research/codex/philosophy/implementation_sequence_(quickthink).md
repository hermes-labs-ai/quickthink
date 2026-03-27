# Implementation Sequence (QuickThink): Tests First or Validators First

## Status
Exploratory decision memo for credit-efficient sequencing.

## Purpose
Decide whether to invest first in new semantic validators or first in targeted experiments.

## Inputs
- Current syntax validator and fallback behavior in runtime.
- Existing eval harness (`scripts/eval_harness/*`).
- Constraint: optimize for limited inference credits.

## Output
Recommended sequence that minimizes wasted implementation effort.

## Option A: Add Validators Now
Pros:
- Immediate stronger guardrails on internal plan quality.
- Potentially cleaner behavior under malformed plans.

Cons:
- Risk of overfitting validator rules to unmeasured assumptions.
- Engineering time may be spent on checks that do not correlate with outcome quality.

## Option B: Run Targeted Tests First
Pros:
- Establishes empirical signal before architecture expansion.
- Reveals which semantic dimensions actually matter (curvature mapping).
- Better credit efficiency over medium term.

Cons:
- Short-term uncertainty remains during measurement phase.

## Recommendation
Choose Option B (tests first), then implement minimal validators only where metrics show strong payoff.

## Minimal-Credit Plan
1. Baseline:
- Run small `direct` vs `lite` vs `two_pass` slice (one model, 1-2 runs).
2. Perturbation:
- Introduce controlled edits to `g,c,s,r` in captured plans and compare judged deltas.
3. Curvature map:
- Rank fields by average impact on constraint adherence and format validity.
4. Validator scope:
- Add semantic checks only for high-curvature failure patterns.

## Proposed Gating Rule
Implement a new validator only if:
- It prevents a repeated failure mode in at least two prompt groups.
- It yields measurable quality gain in judged results without unacceptable latency cost.

## Commands
```bash
python3 scripts/eval_harness/run_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --models qwen2.5:1.5b \
  --modes direct,lite,two_pass \
  --runs 1 \
  --out docs/evals/results/run-seq-baseline.jsonl \
  --manifest-out docs/evals/results/manifest-seq-baseline.json
```

```bash
python3 scripts/eval_harness/judge_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --results docs/evals/results/run-seq-baseline.jsonl \
  --out docs/evals/results/judged-seq-baseline.jsonl \
  --backend rule
```

## Limits
- This memo does not change runtime behavior.
- Perturbation tooling is not yet implemented in code; this is a sequencing decision.
