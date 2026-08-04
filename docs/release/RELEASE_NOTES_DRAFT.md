# quickthink v0.2.1

Released: 2026-08-04

## What quickthink is for

quickthink is a local-first CLI and Python library for shaping Ollama-backed LLM calls. It uses routing and a compact plan-then-answer scaffold for prompts that appear multi-step, while sending simpler prompts directly to the selected local model.

## What changed

- Prepared the first PyPI release path with a tag/version guard, distribution build, and package metadata validation before the protected trusted-publisher job can run.
- Added clear install guidance for both the source-only and post-PyPI states.
- Added `quickthink --version` for installed-package identification.
- Synced package, citation, and Zenodo metadata to `0.2.1`.

There are no inference-path changes in this release and no general model-quality improvement claim.

## Install and first result

After the PyPI publish job for this release has succeeded:

```bash
python -m pip install "quickthink==0.2.1"
ollama pull qwen2.5:1.5b
quickthink ask "Give me a 3-step plan to learn SQL basics" --model qwen2.5:1.5b
```

Before publication, install directly from the repository instead:

```bash
python -m pip install "quickthink @ git+https://github.com/hermes-labs-ai/quickthink.git"
```

## Requirements and limits

- Python 3.9 or later, a running local [Ollama](https://ollama.com/) service, and a pulled model are required.
- The supported model profiles are `qwen2.5:1.5b`, `mistral:7b`, and `gemma3:27b`; other models may run but are untuned.
- quickthink is not a hosted API, training framework, or general agent-orchestration platform. It does not verify answer correctness; results remain model- and task-dependent.

## Links

- [Quickstart](https://github.com/hermes-labs-ai/quickthink#5-minute-quickstart)
- [Known limitations](https://github.com/hermes-labs-ai/quickthink/blob/main/docs/KNOWN_LIMITATIONS.md)
- [Release process](https://github.com/hermes-labs-ai/quickthink/blob/main/docs/release/RELEASE_PROCESS.md)
