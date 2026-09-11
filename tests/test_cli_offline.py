"""CLI behaviour that must work without a running Ollama server."""

from typer.testing import CliRunner

from quickthink.cli import app
from quickthink.config import QuickThinkConfig
from quickthink.engine import QuickThinkEngine

# Port 9 (discard) is closed on every CI runner, so a connection is refused immediately.
UNREACHABLE = "http://127.0.0.1:9"

# Longer than the balanced preset's 120-char bypass threshold and scores >1 on the routing regexes,
# so it takes the scaffold path instead of the direct path.
SCAFFOLD_PROMPT = (
    "Design a retry strategy for a flaky payments API: compare exponential backoff versus a circuit "
    "breaker, list the tradeoffs, and return a JSON schema for the config"
)


def test_help_runs_without_ollama() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ask" in result.output


def test_ask_accepts_direct_mode_and_dry_run_makes_no_network_call() -> None:
    result = CliRunner().invoke(
        app,
        ["ask", "what is 2 + 2?", "--mode", "direct", "--ollama-url", UNREACHABLE, "--dry-run"],
    )
    assert result.exit_code == 0, result.output
    assert "[route] mode=direct bypassed=True" in result.output
    assert "model_calls=1" in result.output
    assert "[prompt:answer]\nwhat is 2 + 2?" in result.output


def test_dry_run_lite_shows_scaffold_prompt() -> None:
    prompt = SCAFFOLD_PROMPT
    result = CliRunner().invoke(app, ["ask", prompt, "--ollama-url", UNREACHABLE, "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "[route] mode=lite bypassed=False" in result.output
    assert "[prompt:plan+answer]" in result.output
    assert "Generate a compact internal plan prefix" in result.output


def test_dry_run_two_pass_lists_both_calls() -> None:
    prompt = SCAFFOLD_PROMPT
    result = CliRunner().invoke(
        app, ["ask", prompt, "--mode", "two_pass", "--ollama-url", UNREACHABLE, "--dry-run"]
    )
    assert result.exit_code == 0, result.output
    assert "model_calls=2" in result.output
    assert "[prompt:plan]" in result.output
    assert "[prompt:answer]" in result.output


def test_ask_invalid_mode_rejected() -> None:
    result = CliRunner().invoke(app, ["ask", "hello", "--mode", "turbo"])
    assert result.exit_code != 0
    assert "mode must be one of: lite, two_pass, direct" in result.output


def test_ask_reports_unreachable_ollama_cleanly() -> None:
    result = CliRunner().invoke(app, ["ask", "hello", "--ollama-url", UNREACHABLE])
    assert result.exit_code == 2
    assert result.exception is None or isinstance(result.exception, SystemExit)
    assert "error: Ollama request to http://127.0.0.1:9 failed" in result.output
    assert "ollama serve" in result.output


def test_engine_preview_matches_run_routing(monkeypatch) -> None:
    cfg = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    cfg.mode = "lite"
    cfg.bypass_short_prompts = False
    cfg.adaptive_routing = False
    engine = QuickThinkEngine(cfg)

    sent: list[str] = []

    def fake_generate(**kwargs):  # type: ignore[no-untyped-def]
        sent.append(str(kwargs.get("prompt", "")))
        return {"response": "[P]g:x;c:y;s:z;r:k\n[A]ok"}

    monkeypatch.setattr(engine.client, "generate", fake_generate)

    preview = engine.preview("Compare two retry strategies")
    result = engine.run("Compare two retry strategies")

    assert preview.bypassed is result.bypassed
    assert preview.route_score == result.route_score
    assert preview.selected_plan_budget == result.selected_plan_budget
    assert [text for _, text in preview.prompts] == sent
