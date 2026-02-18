# Version Notes

## v0.1.0 (main)
- Two-pass scaffold by default:
  1) Generate compact plan
  2) Generate answer using plan
- Strong control over plan structure.
- Higher overhead due to two model calls.

## v0.2.0-lite-inline (branch: codex/lite-inline-v1)
- `lite` mode is now default.
- One-pass inline protocol:
  - `[P]g:...;c:...;s:...;r:...`
  - `[A]final answer`
- Middleware extracts/hides `[P]` from UI and can log it.
- `two_pass` mode retained for A/B comparisons.
- `bench` now compares `lite` vs `two_pass` vs `direct`.

## Practical Difference
- `two_pass`: more control, more latency.
- `lite`: closer to product vision, lower orchestration overhead.

## Recommendation
- Use `lite` for product default.
- Keep `two_pass` as evaluation/control lane until benchmarks stabilize.
