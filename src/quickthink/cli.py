from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .config import MODEL_PROFILES, QuickThinkConfig
from .engine import QuickThinkEngine
from .ui_server import serve_ui

app = typer.Typer(help="Compressed planning scaffold for local LLMs")


@app.command()
def list_models() -> None:
    for model, profile in MODEL_PROFILES.items():
        typer.echo(f"{model} -> {json.dumps(profile)}")


@app.command()
def ask(
    prompt: str = typer.Argument(..., help="User prompt"),
    model: str = typer.Option("qwen2.5:1.5b", help="Ollama model"),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL"),
    mode: str = typer.Option("lite", help="Execution mode: lite or two_pass"),
    show_plan: bool = typer.Option(False, help="Show compressed plan in terminal output"),
    show_route: bool = typer.Option(False, help="Show routing diagnostics"),
    log_file: Optional[Path] = typer.Option(None, help="Optional JSONL log file"),
    bypass_short_prompts: bool = typer.Option(True, help="Skip plan stage for short prompts"),
    continuity_hint: Optional[str] = typer.Option(None, help="Optional tiny continuity hint"),
) -> None:
    if mode not in {"lite", "two_pass"}:
        raise typer.BadParameter("mode must be 'lite' or 'two_pass'")
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config.bypass_short_prompts = bypass_short_prompts
    config.mode = mode
    config.continuity_hint = continuity_hint
    engine = QuickThinkEngine(config)

    result = engine.run(prompt)

    if show_route:
        typer.echo(
            f"[route] mode={result.mode} bypassed={result.bypassed} score={result.route_score} "
            f"plan_budget={result.selected_plan_budget} repaired={result.plan_repaired}"
        )
    if show_plan and result.plan:
        typer.echo(f"[plan] {result.plan}")
    typer.echo(result.answer)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "prompt": prompt,
                        "model": model,
                        "mode": result.mode,
                        "answer": result.answer,
                        "plan": result.plan,
                        "bypassed": result.bypassed,
                        "route_score": result.route_score,
                        "selected_plan_budget": result.selected_plan_budget,
                        "plan_repaired": result.plan_repaired,
                        "plan_latency_ms": round(result.plan_latency_ms, 2),
                        "answer_latency_ms": round(result.answer_latency_ms, 2),
                        "total_latency_ms": round(result.total_latency_ms, 2),
                    }
                )
                + "\n"
            )


@app.command()
def bench(
    prompt: str = typer.Argument(..., help="Benchmark prompt"),
    model: str = typer.Option("qwen2.5:1.5b", help="Ollama model"),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL"),
    runs: int = typer.Option(3, min=1, max=20, help="Number of runs per mode"),
) -> None:
    lite_latencies: list[float] = []
    two_pass_latencies: list[float] = []
    direct_latencies: list[float] = []

    config_lite = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config_lite.mode = "lite"
    engine_lite = QuickThinkEngine(config_lite)
    for _ in range(runs):
        lite_latencies.append(engine_lite.run(prompt).total_latency_ms)

    config_two_pass = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config_two_pass.mode = "two_pass"
    engine_two_pass = QuickThinkEngine(config_two_pass)
    for _ in range(runs):
        two_pass_latencies.append(engine_two_pass.run(prompt).total_latency_ms)

    config_direct = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config_direct.mode = "lite"
    config_direct.bypass_short_prompts = True
    config_direct.adaptive_routing = False
    config_direct.bypass_char_threshold = 100_000
    engine_direct = QuickThinkEngine(config_direct)
    for _ in range(runs):
        direct_latencies.append(engine_direct.run(prompt).total_latency_ms)

    avg_lite = sum(lite_latencies) / len(lite_latencies)
    avg_two_pass = sum(two_pass_latencies) / len(two_pass_latencies)
    avg_direct = sum(direct_latencies) / len(direct_latencies)

    typer.echo(f"model={model}")
    typer.echo(f"avg_lite_ms={avg_lite:.2f}")
    typer.echo(f"avg_two_pass_ms={avg_two_pass:.2f}")
    typer.echo(f"avg_direct_ms={avg_direct:.2f}")
    typer.echo(f"lite_overhead_ms={avg_lite-avg_direct:.2f}")
    typer.echo(f"two_pass_overhead_ms={avg_two_pass-avg_direct:.2f}")


@app.command()
def ui(
    host: str = typer.Option("127.0.0.1", help="Bind host"),
    port: int = typer.Option(7860, min=1, max=65535, help="Bind port"),
    open_browser: bool = typer.Option(True, help="Open UI in browser on startup"),
) -> None:
    serve_ui(host=host, port=port, open_browser=open_browser)


if __name__ == "__main__":
    app()
