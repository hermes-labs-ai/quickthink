# QuickThink Owner Notebook: Technical Memory, GTM Orchestration, and Execution Plan (2026-02-26)

## Purpose
This is the long-term internal notebook for QuickThink. It is written so future-you can reopen it in 1-5 years and recover:
- what the system is,
- what was tested,
- what actually worked,
- where it failed,
- how to commercialize it in concrete steps.

## Recommended Project Label
Use this exact label in your own organization system:

**QuickThink Product Initiative (R&D Stage)**

Rationale:
- Not a pure experiment anymore (replicated lane winners, significance evidence, release gates, hardening work).
- Not fully productized yet (shared/global defaults still fail strict deployment criteria).

---

## Section 1: What QuickThink Is Right Now

QuickThink is a local LLM inference-control layer with:
1. runtime scaffolding (`lite`, `two_pass`, routing, lane policy),
2. reproducible evaluation harness,
3. deployment gate logic (`PASS` / `FAIL` / `INCONCLUSIVE`) with auditable reasons.

It is strongest today as:
- a reliability/latency control layer for local models,
- especially where strict output requirements and auditability matter.

It is not yet:
- a universal scaffold solution that safely generalizes across all models and task classes.

---

## Section 2: Architecture Memory (How It Works)

## 2.1 Runtime paths
- Direct path: raw model answer, no scaffold.
- `lite` path: single generation with inline protocol:
  - `[P]g:...;c:...;s:...;r:...`
  - `[A]final answer`
- `two_pass` path:
  - first call generates plan,
  - validator/repair fallback,
  - second call generates final answer with plan as hidden context.

Primary files:
- `src/quickthink/engine.py`
- `src/quickthink/prompts.py`
- `src/quickthink/plan_grammar.py`
- `src/quickthink/inline_protocol.py`

## 2.2 Plan grammar contract
Canonical compact plan grammar:
- `g:<goal>;c:<constraints>;s:<strategy>;r:<risk_check>`
- lowercase, strict key order, no spaces, bounded token budget.

Validator behavior:
- malformed plan in `lite` -> deterministic fallback plan.
- malformed plan in `two_pass` -> repair attempt, then deterministic fallback.

## 2.3 Routing and lane policy
Routing controls:
- complexity score from regex heuristics and prompt length,
- bypass logic for short/low-complexity prompts,
- adaptive plan budget selection.

Strict lane control:
- `lane_policy=strict_safe` forces direct path for strict-format prompts.

Primary files:
- `src/quickthink/routing.py`
- `src/quickthink/config.py`

## 2.4 Eval and deployment gate stack
Canonical run/judge/decision tools:
- `scripts/eval_harness/run_variant_gate.py`
- `scripts/eval_harness/make_gate_decision.py`
- `docs/evals/deployment_gate_2026.md`

Gate criteria (deployment):
- non-tie win-rate threshold,
- p-value threshold,
- latency delta threshold,
- minimum lift-case count,
- no severe group regression.

---

## Section 3: Experiment Tracks Explained (No Missing Context)

## 3.1 Main optimization track (core engineering lane)
Intent:
- evolve compact scaffold variants and routing behaviors,
- validate against direct baselines on controlled prompt sets,
- freeze lane-specific winners for release.

Representative artifacts:
- `experiments-local/validations/frozen-20260218-20260218-234618/*`
- `experiments-local/model_champions.json`
- `experiments-local/model-scaffolds-and-decisions.md`

## 3.2 Philosophy track (concept-driven variant design)
Intent:
- test concept-level scaffold rules as behavioral hypotheses, not style tweaks.
- evaluate whether conceptual prompt structure can improve outcomes.

The 12 concept variants:
1. `v01_anchor_dual_relation`: explicit task-answer anchoring.
2. `v02_language_game_moves`: legal-move framing (Wittgenstein language-games).
3. `v03_horizon_fusion_guard`: separate user horizon from model priors unless evidence supports merge.
4. `v04_negative_capability`: preserve ambiguity under underconstraint.
5. `v05_curvature_first`: prioritize high-curvature tokens (constraints/strategy).
6. `v06_contradiction_probe`: internal contradiction check before answer.
7. `v07_boundary_literalism`: treat output format as hard boundary.
8. `v08_continuity_memory_light`: preserve template/policy terms with continuity hints.
9. `v09_adversarial_paraphrase_resilience`: stabilize intent under wording variation.
10. `v10_minimal_commitment`: avoid unsupported claims.
11. `v11_repair_then_realize`: repair semantics before answer generation.
12. `v12_constraint_priority_order`: prioritize format -> explicit constraints -> correctness narration.

Canonical source:
- `docs/research/codex/experiments/phenomenology_variants_2026-02-25.json`

## 3.3 What “language game moves” means here
From Wittgenstein-inspired framing in this repo:
- prompts are treated as rule-governed interaction spaces,
- variant explicitly asks model to choose legal moves relative to user-task terms,
- goal is to reduce unanchored/irrelevant language actions.

Repo semantics:
- variant rule text: `interpret_request_as_language_game;select_legal_moves_only;map_each_move_to_user_task_terms`.

## 3.4 Assumption-challenge track (falsification-first)
Intent:
- challenge optimism and theory lock-in,
- test counter-assumptions like judge artifacts, subgroup collapse, weak cross-model transfer, and variance-noise ambiguity.

Counter-assumptions explicitly tested include:
1. structural prompts may have smaller effect than plain task clarity,
2. some gains may be judge-alignment artifact,
3. gains may hide regressions in harder subsets,
4. format compliance may rise while semantic success falls,
5. cross-model transfer may be weak.

Canonical sources:
- `experiments-local/philo_assumption_challenge_2026-02-25/README.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/counter_assumptions_test_matrix.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/prompt_for_philo_researcher_1.md`

---

## Section 4: Quantitative State of Evidence

## 4.1 Lane winners (frozen validation)
From frozen revalidation:
- qwen winner (`lite.r02.m04.logic_check`):
  - score delta: `+0.542`
  - latency delta: `-897.12 ms`
  - n: `48`
- llama winner (`lite.r01.v03.concise`):
  - score delta: `+0.375`
  - latency delta: `-394.05 ms`
  - n: `48`

Sources:
- `experiments-local/validations/frozen-20260218-20260218-234618/FROZEN_WINNERS_REPORT.md`
- `experiments-local/model_champions.json`

## 4.2 Significance replication (`n=8` repeats)
- qwen lane winner:
  - score delta: `+0.3073`
  - latency delta: `-242.05 ms`
  - non-tie win rate: `0.693`
  - p-value: `0.00108`
  - paired probes: `192`
- llama lane winner:
  - score delta: `+0.2604`
  - latency delta: `-462.42 ms`
  - non-tie win rate: `0.645`
  - p-value: `0.00353`
  - paired probes: `192`

Source:
- `experiments-local/validations/significance-2026-02-19/SIGNIFICANCE_SUMMARY.md`

## 4.3 Shared scaffold gate outcomes (current blocker)
Gate decisions:
- `shared_scaffold_gate_stable2`: `18 FAIL / 18`
- `shared_scaffold_gate_strict2`: `8 FAIL / 8`
- `shared_scaffold_gate_lanefallback2`: `12 FAIL / 18`, `6 INCONCLUSIVE / 18`

Most frequent blockers:
- `insufficient_lift_cases`
- `pvalue_above_threshold`
- `group_regression_detected` (especially strict/instruction constraints)

Sources:
- `experiments-local/results/shared_scaffold_gate_stable2_20260225-135515/gate_decision.json`
- `experiments-local/results/shared_scaffold_gate_strict2_20260225-193357/gate_decision.json`
- `experiments-local/results/shared_scaffold_gate_lanefallback2_20260225-201305/gate_decision.json`

## 4.4 Philosophy significance run (qwen top3 n=15)
- `v02_language_game_moves`: `+0.2944`, p=`0.00427`, latency `-582.23 ms`
- `v03_horizon_fusion_guard`: `+0.2333`, p=`0.03962`, latency `-719.07 ms`
- `v04_negative_capability`: `+0.1556`, p=`0.10064`, structured-output regression warning

Source:
- `docs/research/codex/experiments/phenomenology_run_2026-02-25_top3_n15/summary.md`

## 4.5 Assumption-challenge readout
qwen `n=3`:
- several strong directional deltas,
- but repeated structured-output regression warnings (11 warnings in run summary).

mistral `n=3`:
- broad positive deltas with strong p-values on many variants,
- still some structured-output regressions (3 warnings).

Sources:
- `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n3_full/summary.json`
- `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n3_full/summary.json`

---

## Section 5: Main Problems in the Current Track (Concrete)

1. **Strict-format fragility**:
- shared variants often regress instruction-constrained outputs.

2. **Lift-case bottleneck**:
- many promising lanes fail because lift-case counts miss gate minimums.

3. **Routing confound risk**:
- bypass behavior can mask real scaffold path performance if not audited.

4. **Heuristic classifier limits**:
- strict-format inference relies on regex/task-class heuristics.

5. **Backend stability and contention sensitivity**:
- local model contention can distort latency and stall long eval runs.

6. **Judge dependency**:
- alternate judge attempt produced fallback rows in at least one trial; decision-grade independence still incomplete.

7. **Lane coverage gap**:
- some model lanes remain unstable/inconclusive for rollout-level claims.

8. **Runtime maintainability debt**:
- UI/server composition still somewhat monolithic for scale.

---

## Section 6: Confidence Model

- `C4` High: replicated + statistically significant + decision-gate aligned.
- `C3` Medium-High: strong evidence with scope limits.
- `C2` Medium: directional, with unresolved confounds.
- `C1` Low: exploratory only.
- `C0` Very Low: anecdotal only.

Current confidence by claim:
1. Lane-specific winners beat direct on tested lanes: `C4`.
2. Universal shared scaffold ready now: `C0` (current evidence contradicts).
3. Philosophy variants contain promotable ideas: `C3`.
4. Immediate pilot commercialization viability: `C3`.

---

## Section 7: GTM Orchestration (50 -> 20 -> 5)

## 7.1 ICP definition (for this stage)
Ideal early customer profile:
- building production AI applications (agents/RAG/workflows),
- has strict output or compliance-sensitive requirements,
- feels pain from quality variance, formatting failures, and latency tails,
- is open to integrating middleware control/eval layers.

## 7.2 Universe of 50 organizations
This list is intentionally practical: each org website was checked reachable during this pass.

### A) Agent platforms / self-hosted AI products
1. Open WebUI - <https://openwebui.com>
2. AnythingLLM - <https://anythingllm.com>
3. Dify - <https://dify.ai>
4. FlowiseAI - <https://flowiseai.com>
5. Langflow - <https://www.langflow.org>
6. LibreChat - <https://www.librechat.ai>
7. LobeChat - <https://lobehub.com>
8. Continue - <https://continue.dev>
9. LM Studio - <https://lmstudio.ai>
10. LocalAI - <https://localai.io>
11. Ollama - <https://ollama.com>
12. Jan - <https://jan.ai>
13. Open Interpreter - <https://openinterpreter.com>
14. Ragie - <https://www.ragie.ai>

### B) LLM reliability / eval / gateway tooling
15. Langfuse - <https://langfuse.com>
16. Weights & Biases - <https://wandb.ai>
17. Arize AI - <https://arize.com>
18. Humanloop - <https://humanloop.com>
19. Helicone - <https://www.helicone.ai>
20. Portkey - <https://portkey.ai>
21. Promptfoo - <https://promptfoo.dev>
22. Traceloop - <https://traceloop.com>
23. Parea AI - <https://parea.ai>
24. Athina AI - <https://athina.ai>

### C) RAG/data infrastructure ecosystems
25. Qdrant - <https://qdrant.tech>
26. Weaviate - <https://weaviate.io>
27. Pinecone - <https://pinecone.io>
28. Zilliz - <https://zilliz.com>
29. Chroma - <https://trychroma.com>
30. LanceDB - <https://lancedb.com>
31. Unstructured - <https://unstructured.io>
32. deepset - <https://deepset.ai>
33. LlamaIndex - <https://www.llamaindex.ai>
34. LangChain - <https://www.langchain.com>
35. MindsDB - <https://mindsdb.com>
36. Elastic - <https://www.elastic.co>
37. Redis - <https://redis.io>
38. Neo4j - <https://neo4j.com>
39. Databricks - <https://databricks.com>
40. Snowflake - <https://www.snowflake.com>

### D) Enterprise AI platforms (possible partner/distribution channel)
41. Glean - <https://www.glean.com>
42. Writer - <https://writer.com>
43. Cohere - <https://cohere.com>
44. Mistral AI - <https://mistral.ai>
45. Together AI - <https://www.together.ai>
46. Fireworks AI - <https://fireworks.ai>
47. Modal - <https://modal.com>
48. Anyscale - <https://www.anyscale.com>
49. Baseten - <https://www.baseten.co>
50. Replicate - <https://replicate.com>

## 7.3 Top 20 best fit for your current stage
Selection criteria:
- local/self-hosted alignment,
- explicit reliability/eval pain,
- integration feasibility for a small fast-moving team,
- realistic partnership/access likelihood.

Top 20:
1. Open WebUI
2. AnythingLLM
3. Dify
4. FlowiseAI
5. Langflow
6. LibreChat
7. Ollama
8. LocalAI
9. Continue
10. Langfuse
11. Helicone
12. Portkey
13. Promptfoo
14. Qdrant
15. Weaviate
16. LlamaIndex
17. deepset
18. MindsDB
19. Ragie
20. Traceloop

## 7.4 Top 5 must-contact now
These are highest immediate leverage for your current capability profile:

1. Open WebUI
- Why now: explicit self-hosted platform + local model ecosystem overlap.
- Website: <https://openwebui.com>
- GitHub: <https://github.com/open-webui/open-webui>
- LinkedIn company search: <https://www.linkedin.com/search/results/companies/?keywords=Open%20WebUI>
- LinkedIn people search (founder/product): <https://www.linkedin.com/search/results/people/?keywords=Open%20WebUI%20founder%20product>

2. AnythingLLM (Mintplex Labs)
- Why now: all-in-one AI app product with strong quality/format sensitivity.
- Website: <https://anythingllm.com>
- GitHub: <https://github.com/Mintplex-Labs/anything-llm>
- LinkedIn company search: <https://www.linkedin.com/search/results/companies/?keywords=AnythingLLM>
- LinkedIn people search: <https://www.linkedin.com/search/results/people/?keywords=AnythingLLM%20founder%20engineering>

3. Dify
- Why now: agent workflow builder; direct fit for routing + eval gating value.
- Website: <https://dify.ai>
- GitHub: <https://github.com/langgenius/dify>
- LinkedIn company search: <https://www.linkedin.com/search/results/companies/?keywords=Dify%20AI>
- LinkedIn people search: <https://www.linkedin.com/search/results/people/?keywords=Dify%20AI%20product%20engineering>

4. FlowiseAI
- Why now: open source agent orchestration audience likely values reliable scaffold policies.
- Website: <https://flowiseai.com>
- GitHub: <https://github.com/FlowiseAI/Flowise>
- LinkedIn company search: <https://www.linkedin.com/search/results/companies/?keywords=Flowise>
- LinkedIn people search: <https://www.linkedin.com/search/results/people/?keywords=Flowise%20founder%20maintainer>

5. Langfuse
- Why now: eval/observability distribution channel for showcasing measurable lift.
- Website: <https://langfuse.com>
- GitHub: <https://github.com/langfuse/langfuse>
- LinkedIn company search: <https://www.linkedin.com/search/results/companies/?keywords=Langfuse>
- LinkedIn people search: <https://www.linkedin.com/search/results/people/?keywords=Langfuse%20product%20partnerships>

## 7.5 Outreach motion (exact)
Sequence for each top-5 target:
1. Open issue/discussion: 1-paragraph problem framing + measured deltas.
2. DM/email to product or engineering lead with a 10-day pilot offer.
3. Pilot scope:
   - 1 strict-format workflow,
   - 1 reasoning workflow,
   - before/after metrics (score delta, strict-format pass delta, p95 latency delta).
4. Deliverables:
   - short integration guide,
   - result summary markdown,
   - rollback-safe config.

Initial outbound message skeleton:
- Subject: `Proposal: strict-output reliability uplift for <Company> local/agent workflows`
- Body:
  - one sentence on observed failure mode,
  - one sentence with your validated deltas,
  - pilot scope and timeline,
  - concrete ask for 30-minute technical fit call.

---

## Section 8: 30/60/90 Plan (Manager-Grade Detail)

## First 30 days: Product proof package
Objectives:
1. Make pilot-grade proof artifact impossible to misunderstand.
2. Close highest-risk measurement confounds.

Deliverables:
1. Standardized benchmark packet:
   - bypass rate per mode,
   - per-group deltas,
   - lift-case table,
   - gate decision output.
2. Strict-format hardening iteration:
   - expand strict prompt fixtures,
   - run strict-safe lane defaults,
   - record explicit failure taxonomy.
3. Pilot collateral:
   - one-page technical brief,
   - one-page business value brief,
   - integration checklist.

KPIs:
- 3 completed pilot conversations.
- 2 agreed technical evaluations.
- 1 published reproducible benchmark packet.

## Day 31-60: Pilot execution and close
Objectives:
1. Convert interest into live pilot data.
2. Prove repeatability across at least two external environments.

Deliverables:
1. Two pilot implementations with:
   - baseline snapshot,
   - post-integration snapshot,
   - signed-off metric deltas.
2. Lane policy recommendations by use case:
   - strict-format,
   - reasoning,
   - continuity.
3. Risk memo:
   - unresolved failure modes,
   - mitigation backlog and ETA.

KPIs:
- 2 pilots live.
- >=1 pilot with measured strict-format reliability lift.
- >=1 pilot willing to provide testimonial/reference (private is fine).

## Day 61-90: Packaging and scale decision
Objectives:
1. Decide whether to remain services-first or launch productized offer.
2. Prepare funding-or-bootstrap fork decision with real traction data.

Deliverables:
1. Offer definition:
   - Pilot package (fixed scope),
   - Subscription or license expansion option.
2. Pricing test:
   - 2 pricing hypotheses tested with live prospects.
3. Funding decision memo:
   - bootstrap runway model,
   - incubator/fund path if acceleration needed.

KPIs:
- 1 paid engagement.
- 5 qualified pipeline opportunities.
- decision on bootstrap-only vs hybrid fundraising.

---

## Section 9: Bootstrap vs Funding (Decision Framework)

## 9.1 Bootstrap-first is viable if all are true
1. You can secure 1-2 paid pilots in <90 days.
2. Scope remains focused on 1-2 model lanes and strict use cases.
3. Infrastructure costs remain modest (local/Ollama-first posture).

## 9.2 Fundraising is justified if any are true
1. Pipeline grows faster than delivery capacity.
2. You need rapid enterprise hardening (security/compliance/integration depth).
3. A platform distribution partnership requires scaling headcount quickly.

## 9.3 Accelerator and startup-program options
1. Y Combinator - <https://www.ycombinator.com>
2. Techstars accelerators - <https://www.techstars.com/accelerators>
3. Alchemist Accelerator - <https://www.alchemistaccelerator.com>
4. Antler - <https://www.antler.co>
5. Berkeley SkyDeck - <https://skydeck.berkeley.edu>
6. NVIDIA Inception - <https://www.nvidia.com/en-us/startups/>
7. AWS Activate - <https://aws.amazon.com/activate/>
8. Google for Startups Cloud - <https://cloud.google.com/startup>
9. Microsoft Founders Hub - <https://startups.microsoft.com/>
10. OpenAI Startup Fund - <https://openai.fund>

Practical recommendation:
- run bootstrap + pilot sales first,
- apply to 1-2 acceleration programs only after initial pilot proof packet is complete.

---

## Section 10: Immediate Operating Checklist (Next 14 Days)

1. Freeze this notebook as your canonical decision memory.
2. Build a one-page external pilot brief from this document.
3. Start outreach to top-5 targets (minimum 2 touches per target).
4. Execute one new strict-format-focused benchmark with bypass reporting enforced.
5. Create weekly dashboard:
   - outreach count,
   - meetings booked,
   - pilots active,
   - benchmark deltas by lane.

---

## Section 11: Sources

## Internal (repo)
- `docs/research/QUICKTHINK_PRODUCT_INITIATIVE_EXECUTIVE_REPORT_2026-02-26.md`
- `experiments-local/validations/frozen-20260218-20260218-234618/FROZEN_WINNERS_REPORT.md`
- `experiments-local/validations/significance-2026-02-19/SIGNIFICANCE_SUMMARY.md`
- `experiments-local/results/shared_scaffold_gate_stable2_20260225-135515/gate_decision.json`
- `experiments-local/results/shared_scaffold_gate_strict2_20260225-193357/gate_decision.json`
- `experiments-local/results/shared_scaffold_gate_lanefallback2_20260225-201305/gate_decision.json`
- `docs/research/codex/experiments/phenomenology_variants_2026-02-25.json`
- `experiments-local/philo_assumption_challenge_2026-02-25/counter_assumptions_test_matrix.md`
- `src/quickthink/engine.py`
- `src/quickthink/prompts.py`
- `src/quickthink/routing.py`

## External (market/program context and target orgs)
- Target org websites listed in Section 7.
- Program/funding websites listed in Section 9.
