# Known Limitations

Use this list when evaluating fit before production use.

- Model-specific behavior: gains are not universal across model families.
- Prompt-distribution sensitivity: benchmark results depend on prompt sets and judge settings.
- Latency sensitivity: output length, hardware, and concurrent load can materially change latency.
- No hard correctness guarantee: scaffolding can improve consistency but does not guarantee correctness.
- Local runtime dependency: requires a healthy local Ollama environment for supported workflows.
- CI scope: no live-Ollama integration tests run in CI yet.

Before external claims, follow `docs/PUBLIC_CLAIMS_POLICY.md` and include full benchmark context.
