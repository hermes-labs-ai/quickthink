from __future__ import annotations

from types import SimpleNamespace

import quickthink.ui_server as ui_server


class _DummyEngine:
    last_config = None

    def __init__(self, config):
        type(self).last_config = config

    def run(self, _prompt: str):
        return SimpleNamespace(
            answer="ok",
            plan=None,
            mode="lite",
            bypassed=False,
            route_score=0,
            selected_plan_budget=6,
            plan_repaired=False,
            plan_latency_ms=0.0,
            answer_latency_ms=1.0,
            total_latency_ms=1.0,
        )


def test_run_eval_mode_passes_lane_policy(monkeypatch) -> None:
    monkeypatch.setattr(ui_server, "QuickThinkEngine", _DummyEngine)
    ui_server._run_eval_mode(
        prompt="json only: {\"ok\":true}",
        model="qwen2.5:1.5b",
        mode="lite",
        ollama_url="http://localhost:11434",
        lane_policy="strict_safe",
        bypass_short_prompts=False,
        continuity_hint=None,
    )
    assert _DummyEngine.last_config is not None
    assert _DummyEngine.last_config.lane_policy == "strict_safe"


def test_run_eval_mode_direct_sets_forced_direct_flags(monkeypatch) -> None:
    monkeypatch.setattr(ui_server, "QuickThinkEngine", _DummyEngine)
    ui_server._run_eval_mode(
        prompt="test",
        model="qwen2.5:1.5b",
        mode="direct",
        ollama_url="http://localhost:11434",
        lane_policy="default",
        bypass_short_prompts=False,
        continuity_hint=None,
    )
    assert _DummyEngine.last_config is not None
    assert _DummyEngine.last_config.mode == "direct"
    assert _DummyEngine.last_config.adaptive_routing is False
    assert _DummyEngine.last_config.bypass_short_prompts is True
