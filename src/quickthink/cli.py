from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib.metadata import version as package_version
from pathlib import Path
from typing import NoReturn, Optional

import httpx
import typer

from .config import MODEL_PROFILES, PRESET_PROFILES, SUPPORTED_MODELS, QuickThinkConfig
from .engine import QuickThinkEngine
from .ui_server import serve_ui

app = typer.Typer(help="Compressed planning scaffold for local LLMs")

MODES = ("lite", "two_pass", "direct")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(package_version("quickthink"))
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the installed quickthink version and exit.",
    ),
) -> None:
    """Compressed planning scaffold for local LLMs."""


@app.command()
def list_models() -> None:
    for model, profile in MODEL_PROFILES.items():
        typer.echo(f"{model} -> {json.dumps(profile)}")


@app.command()
def list_presets() -> None:
    for preset, profile in PRESET_PROFILES.items():
        typer.echo(f"{preset} -> {json.dumps(profile)}")


@app.command()
def compatibility() -> None:
    for model in SUPPORTED_MODELS:
        typer.echo(model)


@app.command()
def ask(
    prompt: str = typer.Argument(..., help="User prompt"),
    model: str = typer.Option("qwen2.5:1.5b", help="Ollama model"),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL"),
    mode: str = typer.Option("lite", help="Execution mode: lite, two_pass, or direct"),
    preset: str = typer.Option("balanced", help="Preset profile: fast, balanced, strict"),
    show_plan: bool = typer.Option(False, help="Show compressed plan in terminal output"),
    show_route: bool = typer.Option(False, help="Show routing diagnostics"),
    log_file: Optional[Path] = typer.Option(None, help="Optional JSONL log file"),
    bypass_short_prompts: bool = typer.Option(True, help="Skip plan stage for short prompts"),
    continuity_hint: Optional[str] = typer.Option(None, help="Optional tiny continuity hint"),
    lane_policy: str = typer.Option("default", help="Lane policy: default or strict_safe"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Resolve routing and print the prompt(s) that would be sent to Ollama, without calling it",
    ),
) -> None:
    if mode not in MODES:
        raise typer.BadParameter("mode must be one of: lite, two_pass, direct")
    if preset not in PRESET_PROFILES:
        raise typer.BadParameter("preset must be one of: fast, balanced, strict")
    if lane_policy not in {"default", "strict_safe"}:
        raise typer.BadParameter("lane-policy must be 'default' or 'strict_safe'")
    config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    config.apply_preset(preset)
    config.bypass_short_prompts = bypass_short_prompts
    config.mode = mode
    config.continuity_hint = continuity_hint
    config.lane_policy = lane_policy
    engine = QuickThinkEngine(config)

    if dry_run:
        preview = engine.preview(prompt)
        typer.echo(
            f"[route] mode={preview.mode} bypassed={preview.bypassed} score={preview.route_score} "
            f"plan_budget={preview.selected_plan_budget} model_calls={preview.model_calls} model={model}"
        )
        for stage, text in preview.prompts:
            typer.echo(f"[prompt:{stage}]")
            typer.echo(text)
        return

    try:
        result = engine.run(prompt)
    except httpx.HTTPError as exc:
        _ollama_error(exc, ollama_url=ollama_url, model=model)

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
                        "preset": config.preset,
                        "mode": result.mode,
                        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
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


def _ollama_error(exc: httpx.HTTPError, *, ollama_url: str, model: str) -> NoReturn:
    typer.echo(
        f"error: Ollama request to {ollama_url} failed ({exc.__class__.__name__}: {exc}).\n"
        f"Start Ollama with `ollama serve` and make sure the model is available with `ollama pull {model}`.",
        err=True,
    )
    raise typer.Exit(code=2)


def _bench_modes(
    *,
    prompt: str,
    model: str,
    ollama_url: str,
    runs: int,
    preset: str,
    lane_policy: str,
    lite_latencies: list[float],
    two_pass_latencies: list[float],
    direct_latencies: list[float],
) -> None:
    for mode, latencies in (("lite", lite_latencies), ("two_pass", two_pass_latencies), ("direct", direct_latencies)):
        config = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
        config.apply_preset(preset)
        config.mode = mode
        # Benchmark the configured mode itself: without this, prompts below the preset's
        # bypass threshold or complexity score would silently measure the direct path under
        # a lite/two_pass label. `strict_safe` keeps its own strict-format bypass.
        config.bypass_short_prompts = False
        config.adaptive_routing = False
        config.lane_policy = lane_policy
        engine = QuickThinkEngine(config)
        for _ in range(runs):
            latencies.append(engine.run(prompt).total_latency_ms)


@app.command()
def bench(
    prompt: str = typer.Argument(..., help="Benchmark prompt"),
    model: str = typer.Option("qwen2.5:1.5b", help="Ollama model"),
    ollama_url: str = typer.Option("http://localhost:11434", help="Ollama base URL"),
    runs: int = typer.Option(3, min=1, max=20, help="Number of runs per mode"),
    preset: str = typer.Option("balanced", help="Preset profile: fast, balanced, strict"),
    lane_policy: str = typer.Option("default", help="Lane policy: default or strict_safe"),
) -> None:
    if preset not in PRESET_PROFILES:
        raise typer.BadParameter("preset must be one of: fast, balanced, strict")
    if lane_policy not in {"default", "strict_safe"}:
        raise typer.BadParameter("lane-policy must be 'default' or 'strict_safe'")
    lite_latencies: list[float] = []
    two_pass_latencies: list[float] = []
    direct_latencies: list[float] = []

    try:
        _bench_modes(
            prompt=prompt,
            model=model,
            ollama_url=ollama_url,
            runs=runs,
            preset=preset,
            lane_policy=lane_policy,
            lite_latencies=lite_latencies,
            two_pass_latencies=two_pass_latencies,
            direct_latencies=direct_latencies,
        )
    except httpx.HTTPError as exc:
        _ollama_error(exc, ollama_url=ollama_url, model=model)

    avg_lite = sum(lite_latencies) / len(lite_latencies)
    avg_two_pass = sum(two_pass_latencies) / len(two_pass_latencies)
    avg_direct = sum(direct_latencies) / len(direct_latencies)

    typer.echo(f"model={model}")
    typer.echo(f"preset={preset}")
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
