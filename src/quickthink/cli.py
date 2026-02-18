from __future__ import annotations

import json
from pathlib import Path

import typer

from .config import MODEL_PROFILES, QuickThinkConfig
from .engine import QuickThinkEngine

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
    show_plan: bool = typer.Option(False, help="Show compressed plan in terminal output"),
    show_route: bool = typer.Option(False, help="Show routing diagnostics"),
    log_file: Path | None = typer.Option(None, help="Optional JSONL log file"),
    bypass_short_prompts: bool = typer.Option(True, help="Skip plan stage for short prompts"),
) -> None:
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config.bypass_short_prompts = bypass_short_prompts
    engine = QuickThinkEngine(config)

    result = engine.run(prompt)

    if show_route:
        typer.echo(
            f"[route] bypassed={result.bypassed} score={result.route_score} "
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
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    engine = QuickThinkEngine(config)

    think_latencies: list[float] = []
    no_think_latencies: list[float] = []

    for _ in range(runs):
        result = engine.run(prompt)
        think_latencies.append(result.total_latency_ms)

    config_no_think = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config_no_think.bypass_short_prompts = True
    config_no_think.adaptive_routing = False
    config_no_think.bypass_char_threshold = 100_000
    engine_no_think = QuickThinkEngine(config_no_think)
    for _ in range(runs):
        result = engine_no_think.run(prompt)
        no_think_latencies.append(result.total_latency_ms)

    avg_think = sum(think_latencies) / len(think_latencies)
    avg_no_think = sum(no_think_latencies) / len(no_think_latencies)
    delta = avg_think - avg_no_think

    typer.echo(f"model={model}")
    typer.echo(f"avg_quickthink_ms={avg_think:.2f}")
    typer.echo(f"avg_direct_ms={avg_no_think:.2f}")
    typer.echo(f"delta_ms={delta:.2f}")


if __name__ == "__main__":
    app()
