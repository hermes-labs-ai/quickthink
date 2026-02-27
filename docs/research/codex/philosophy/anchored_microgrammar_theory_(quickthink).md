# Anchored Microgrammar Theory (QuickThink)

## Status
Exploratory note. Not a normative architecture decision.

## Purpose
Create a philosophical and technical backbone for QuickThink's compressed planning approach, grounded in observed runtime behavior rather than assumptions.

## Inputs
- Runtime plan grammar and validator: `src/quickthink/plan_grammar.py`
- Prompt contracts for plan/answer and inline protocol: `src/quickthink/prompts.py`
- Runtime orchestration and fallback behavior: `src/quickthink/engine.py`
- Inline extraction boundary: `src/quickthink/inline_protocol.py`
- Routing and plan-budget selection: `src/quickthink/routing.py`

## Outputs
- A working theory of why QuickThink's compressed dialect helps.
- Falsifiable hypotheses for follow-up experiments.
- Explicit open questions where current evidence is insufficient.

## Core Claim (Exploratory)
QuickThink's compression works because it is not only token compression. It is relational protocol design:
- A constrained microgrammar defines valid internal moves.
- The same grammar is used at generation and interpretation boundaries.
- The answer path is anchored to a compact internal representation.

In this framing, syntax acts as infrastructure for cognition rather than as cosmetic formatting.

## Observations From Current Code
1. Explicit microgrammar exists: `g:<...>;c:<...>;s:<...>;r:<...>` with tight character constraints and order.
2. Two-sided anchoring exists:
- `two_pass`: plan is generated, validated/repaired, then reinjected into answer prompt.
- `lite`: `[P]...` and `[A]...` are co-generated and parsed by a boundary extractor.
3. Fail-closed fallback exists: invalid plans degrade to a deterministic default plan.
4. Routing controls planning expenditure by complexity score and budget bounds.

## Philosophical Framing
1. Wittgensteinian language-games:
- Meaning is use within a rule-governed practice.
- Here, the microgrammar defines legal operations (`g,c,s,r`) and disallows many ambiguous language moves.
2. Gadamerian relation/horizon:
- Interpretation is not free-floating; it is guided by pre-structure.
- The internal plan acts as pre-structure that narrows the answer horizon.

## Working Model
1. Policy layer:
- High-level constraints, safety style, output contract.
2. Planning layer:
- Compressed microgrammar (`g,c,s,r`) with bounded token budget.
3. Realization layer:
- User-facing answer with hidden planning contract.

Hypothesis: quality improvements come from keeping these layers distinct but coupled through explicit anchors.

## Semantic Curvature Principle (Exploratory)
Definition:
- Semantic curvature is the downstream behavioral sensitivity to small representation edits.

Practical implication:
- High-curvature features must remain explicit in compressed forms.
- Low-curvature features can be aggressively compressed or dropped.

Candidate high-curvature fields in current design:
- `s` (strategy)
- `c` (constraints)

## Failure Modes To Track
1. Syntactically valid but semantically weak plans.
2. Overloaded fields (too much meaning in one slug).
3. Plan-answer drift in `lite` mode when `[P]` is malformed but answer still returns text.
4. Budget-induced semantic collapse where key distinctions disappear.

## Falsifiable Hypotheses
1. H1: Plan grammar anchoring improves constraint adherence on mixed-complexity tasks vs direct mode.
2. H2: Tiny perturbations in `s` produce larger answer deltas than perturbations in `g`.
3. H3: Deterministic fallback plan improves stability under malformed `[P]` outputs.
4. H4: Gains plateau beyond a model-specific plan budget range.

## Commands
Low-cost measurement commands (existing harness):

```bash
python3 scripts/eval_harness/run_variant_gate.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --models qwen2.5:1.5b \
  --runs 2
```

```bash
python3 scripts/eval_harness/judge_suite.py \
  --prompt-set docs/evals/prompt_set.jsonl \
  --results docs/evals/results/<run>.jsonl \
  --out docs/evals/results/<judged>.jsonl \
  --backend rule
```

## Limits
- Current validator checks syntax and token budget, not semantic coherence.
- Current evidence does not yet isolate causal contribution of each field (`g,c,s,r`).
- Conclusions remain provisional until perturbation tests are run.

## Open Questions
1. Which field has the highest curvature per task class?
2. Should microgrammar be domain-adaptive or global?
3. Does `lite` need stronger repair semantics for missing `[P]` beyond current fallback behavior?
4. What is the minimum stable budget per model/preset for non-trivial tasks?
