# AGENT.md

## Purpose
Build **QuickThink** into a production-grade **Linguistically Persistent Cognitive Interface (LPCI)** runtime for local LLM systems.

This project is not a generic wrapper. It is a behavior-control layer:
- compresses reasoning scaffolds,
- preserves cognitive continuity across turns,
- audits behavioral drift,
- improves reliability under real prompt pressure.

## Product Positioning
- Core artifact: local-first inference middleware + CLI/API.
- Distinctive claim: **behavioral consistency from linguistic persistence**, not just better prompt templates.
- User value: higher quality answers from smaller models, with measurable latency and reliability tradeoffs.

## Engineering Stance
- Be helpful, not agreeable.
- Challenge weak assumptions early.
- Prefer measurable claims over stylistic opinions.
- Never ship speculative behavior changes without tests or benchmark instrumentation.

## Non-Negotiables
1. Every behavior change must be testable.
2. Every performance claim must include a benchmark path.
3. Every routing/policy heuristic must be explainable.
4. Silent fallback behavior must be explicit in logs/metadata.
5. Keep default UX simple; expose power via opt-in flags.

## Current Architecture (MVP)
- `src/quickthink/routing.py`: prompt complexity scoring and bypass/plan routing.
- `src/quickthink/plan_grammar.py`: compact plan grammar normalization and validation.
- `src/quickthink/prompts.py`: plan, repair, and answer prompt contracts.
- `src/quickthink/engine.py`: orchestration, repair fallback, latency accounting.
- `src/quickthink/ollama_client.py`: local model transport.
- `src/quickthink/cli.py`: user entrypoint, logging, benchmark command.
- `src/quickthink/ui_server.py`: local-only eval UI sandbox (not core publishable runtime unless promoted).

## Build Direction (vNext)
1. Persistent cognitive state:
   - add optional per-session memory capsule (`goal`, `constraints`, `style`, `open_loops`),
   - feed capsule into planning stage,
   - keep footprint minimal and user-visible.
2. Policy-based routing:
   - replace static regex-only scoring with pluggable routing policies,
   - support profile presets (`fast`, `balanced`, `strict`).
3. Reliability instrumentation:
   - add structured event logs for route decisions and repair causes,
   - emit machine-readable reason codes.
4. Eval harness:
   - create a reproducible prompt suite with expected properties (not fixed wording),
   - track quality + latency deltas over time.
5. API surface:
   - introduce a lightweight local HTTP server mode once CLI semantics stabilize.

## Coding Rules
- Python 3.9+ compatible.
- Type hints required for public functions/classes.
- Keep modules focused; avoid god files.
- Prefer pure functions for scoring/parsing logic.
- No hidden global state for model behavior decisions.
- Keep defaults conservative and deterministic where possible.

## Test Rules
- Unit tests for grammar/routing/prompt contracts are required.
- New heuristics must include counterexample tests.
- For bug fixes: add a failing test first, then fix.
- Benchmark-affecting changes must include before/after numbers in PR notes.

## UX Rules (CLI/API)
- Human output stays concise by default.
- Debug verbosity is opt-in (`--show-plan`, `--show-route`, logs).
- Never leak internal planning unless user explicitly requests it.
- Error messages must include actionable next step.

## Collaboration Protocol For Agents
1. Read this file before editing code.
2. State intended change in one sentence before implementation.
3. If tradeoffs exist, present 2-3 options with a recommendation.
4. If project direction is unclear, ask one focused question, then proceed.
5. Do not widen scope without explicit approval.

## Immediate Backlog
1. Add `SessionState` model + local persistence adapter.
2. Add `route_reason_codes` to `QuickThinkResult` and log output.
3. Add policy abstraction for routing (`BaseRoutingPolicy`).
4. Add `quickthink eval` command for repeatable prompt suites.
5. Add docs page: "What LPCI means in practice."
