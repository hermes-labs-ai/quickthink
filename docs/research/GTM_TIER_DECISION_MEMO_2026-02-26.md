# GTM Tier Decision Memo (Balanced vs No-Loss-First)

## Purpose
Determine which objective tier should be the default go-to-market posture for QuickThink, based on current enterprise AI market conditions and our internal evidence.

## Inputs
External sources reviewed (enterprise/analyst primary pages):
- Gartner GenAI spend forecast (Mar 31, 2025): https://www.gartner.com/en/newsroom/press-releases/2025-03-31-gartner-forecasts-worldwide-genai-spending-to-reach-644-billion-in-2025
- Gartner model-spend forecast (Jul 10, 2025): https://www.gartner.com/en/newsroom/press-releases/2025-07-10-gartner-forecasts-worldwide-end-user-spending-on-generative-ai-models-to-total-us-dollars-14-billion-in-2025
- McKinsey State of AI 2025: https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai
- KPMG AI Pulse Q1 2025: https://kpmg.com/us/en/media/news/q1-ai-pulse-2025.html
- KPMG AI Pulse overview/Q4 2025 context page: https://kpmg.com/us/en/articles/2025/ai-quarterly-pulse-survey.html
- Deloitte State of GenAI in the Enterprise (Q4 press): https://www2.deloitte.com/us/en/pages/about-deloitte/articles/press-releases/state-of-generative-ai.html
- IBM CEO Study 2025: https://www.ibm.com/thought-leadership/institute-business-value/en-us/report/2025-ceo
- WEF Future of Jobs 2025: https://www.weforum.org/press/2025/01/future-of-jobs-report-2025-78-million-new-job-opportunities-by-2030-but-urgent-upskilling-needed-to-prepare-workforces//

Internal evidence reviewed:
- `experiments-local/philo_assumption_challenge_2026-02-25/run_qwen_n8_full/summary.md`
- `experiments-local/philo_assumption_challenge_2026-02-25/run_mistral_n5_full/summary.md`
- `docs/research/DECISION_GATES.md`

## Outputs
- Recommended default tier
- Segment-specific tier mapping
- Decision criteria to apply immediately

## Market read (current)
1. Enterprise spend momentum remains very strong, but buying behavior is becoming more disciplined.
2. Buyers are shifting from exploratory POCs toward production reliability, predictable value, and governance/trust.
3. Data quality, risk, and deployment complexity remain top blockers in scaling AI programs.
4. Practical procurement posture is not "max raw uplift"; it is "reliable uplift with controlled downside."

## Internal evidence fit
1. Internal runs show genuine uplift potential, but not uniform cross-lane behavior.
2. Strong variants can still regress in structured-output lanes on some models.
3. This aligns with a risk-adjusted posture rather than all-in max-gain posture.

## Decision
Default GTM tier should be: `balanced`.

### Why `balanced` as default
1. Best match for broad enterprise demand pattern: measurable gains + trust/governance constraints.
2. Compatible with internal signal shape: positive cross-model opportunities exist, but with lane-specific risk pockets.
3. Defensible commercial narrative: outcome improvement with explicit guardrails.

### Where `no-loss-first` fits
1. Regulated/high-assurance segments (for example: heavily regulated workflows).
2. Security- or policy-sensitive lanes where any subgroup regression is unacceptable.
3. Expansion path from `balanced` once trust is established.

## Packaging recommendation
1. Core package (default): `balanced` gate, explicit lane guardrails.
2. Assurance package: `no-loss-first` gate, stricter promotion criteria.
3. Positioning rule: never claim universal dominance; claim lane-scoped, model-validated uplift.

## Immediate operating policy
Use `docs/research/DECISION_GATES.md` as the normative threshold source:
1. Default to `balanced` for ongoing optimization and recommendations.
2. Promote `no-loss-first` as optional stricter mode for qualified buyers.
3. Require explicit evidence-path citation in every recommendation.

## Commands
No new run command executed for this memo; this is a market-plus-evidence decision synthesis step.

## Limits
1. Some external sources are summary/press pages rather than full raw datasets.
2. Market conditions can shift; this memo should be revisited after major model/platform changes.
3. Final segment targeting still requires customer interviews and pipeline feedback.
