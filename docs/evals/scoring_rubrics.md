# Scoring Rubrics

Use a 0-2 scale per dimension for each response.

## 1) Correctness
- 2: Core task solved correctly with no material errors.
- 1: Partially correct; minor logic/math issue or missing key part.
- 0: Incorrect, contradictory, or non-responsive.

## 2) Constraint Adherence
- 2: All explicit constraints followed (count, words, banned terms, ordering, etc.).
- 1: One minor constraint miss with otherwise useful response.
- 0: Major or multiple constraint violations.

## 3) Format Validity
- 2: Output is valid and parseable in requested format (JSON/YAML/CSV/table/template).
- 1: Mostly correct format with small syntax/shape defect.
- 0: Wrong format or unparseable.

## 4) Verbosity Control
- 2: Length/tone matches instruction exactly (concise when asked, expanded when asked).
- 1: Slightly over/under target but still usable.
- 0: Clear verbosity mismatch or policy break.

## Composite Score
- Per response max: 8
- Recommended pass threshold: 6+ and no zero in any dimension.

## Tie-Break Rules
1. Higher `Constraint Adherence`
2. Higher `Format Validity`
3. Lower latency

## Win-Rate Definition
For pairwise comparisons, a mode records a win when composite score is higher than comparator for the same prompt/run.
- Ignore ties for conditional win-rate.
- Report both: raw win-rate and non-tie win-rate.
