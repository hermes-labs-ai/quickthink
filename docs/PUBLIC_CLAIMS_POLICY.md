# Public Claims Policy

Use this policy for any external statement about `quickthink` performance, quality, or behavior.

## Allowed claim types
Claims must be:
- Measured: based on recorded runs, not anecdotal samples.
- Scoped: limited to the tested models, prompts, and environment.
- Reproducible: accompanied by enough context for others to rerun.

## Prohibited claim patterns
Do not publish claims that are:
- Universal (for example, "always better" or "works for all tasks").
- Generalized beyond tested scope (for example, one model result presented as all-model result).
- Missing measurement context or benchmark conditions.

## Required context for any benchmark/performance claim
Include:
- Model name and version/tag.
- Hardware/runtime environment.
- Prompt set used.
- Number of runs/repeats.
- Judge backend.
- Token caps and generation settings.
- Date and git SHA (if available).
- Link or checksum for released artifacts when referenced publicly.
- Note whether results are from direct, lite, or two_pass mode.

## Claim template
"In our local benchmark on `<date>` (git `<sha>`), using model `<model>`, prompt set `<prompt_set>`, `<runs>` runs, judge backend `<backend>`, and generation settings `<settings>` on `<hardware/runtime>`, we observed `<result>`. This claim is scoped to those conditions."
