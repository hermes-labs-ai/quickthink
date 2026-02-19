# Agent Comms

Lightweight shared communication channel for multiple agents.

## Files
- `docs/agent-comms/log.jsonl`: append-only machine-readable updates
- `docs/agent-comms/THREAD.md`: human-readable rendered thread
- `scripts/ops/agent_comms.py`: helper CLI

## Update Contract
Each update should include:
- agent name
- status (`in_progress`, `blocked`, `done`)
- last action
- notes
- optional open questions
- optional files touched

## Commands
Post update:

```bash
python3 scripts/ops/agent_comms.py post \
  --agent eval-agent \
  --status in_progress \
  --last-action "Validated prompt_set schema" \
  --notes "Starting A/B/C run wiring" \
  --questions "Should multi_turn be single-prompt context-only?" \
  --files docs/evals/prompt_set.jsonl
```

Render thread:

```bash
python3 scripts/ops/agent_comms.py render
```

Tail last updates:

```bash
python3 scripts/ops/agent_comms.py tail -n 15
```

## Coordination Rules
- Always post at task start and task end.
- Use `blocked` with one concrete unblock question.
- Keep notes <= 2 sentences.
- Do not rewrite prior log entries.
