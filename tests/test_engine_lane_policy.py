from quickthink.config import QuickThinkConfig
from quickthink.engine import QuickThinkEngine


def test_strict_safe_routes_to_direct(monkeypatch) -> None:
    cfg = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    cfg.mode = "lite"
    cfg.lane_policy = "strict_safe"
    engine = QuickThinkEngine(cfg)

    calls: list[str] = []

    def fake_generate(**kwargs):  # type: ignore[no-untyped-def]
        calls.append(str(kwargs.get("prompt", "")))
        return {"response": '{"ok":true,"why":"short"}'}

    monkeypatch.setattr(engine.client, "generate", fake_generate)

    result = engine.run('json only: {"ok":true,"why":"short"}')

    assert result.bypassed is True
    assert result.plan is None
    assert result.answer == '{"ok":true,"why":"short"}'
    # Direct path sends raw user prompt, not scaffold prompt.
    assert calls and calls[0].startswith("json only:")


def test_direct_mode_config_routes_to_direct(monkeypatch) -> None:
    cfg = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    cfg.mode = "direct"
    cfg.lane_policy = "default"
    cfg.bypass_short_prompts = False
    cfg.adaptive_routing = False
    engine = QuickThinkEngine(cfg)

    calls: list[str] = []

    def fake_generate(**kwargs):  # type: ignore[no-untyped-def]
        calls.append(str(kwargs.get("prompt", "")))
        return {"response": "direct answer"}

    monkeypatch.setattr(engine.client, "generate", fake_generate)

    result = engine.run("what is 2 + 2?")

    assert result.bypassed is True
    assert result.plan is None
    assert result.answer == "direct answer"
    assert calls and calls[0] == "what is 2 + 2?"


def test_default_lane_policy_keeps_scaffold_path(monkeypatch) -> None:
    cfg = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    cfg.mode = "lite"
    cfg.lane_policy = "default"
    cfg.bypass_short_prompts = False
    cfg.adaptive_routing = False
    engine = QuickThinkEngine(cfg)

    prompts: list[str] = []

    def fake_generate(**kwargs):  # type: ignore[no-untyped-def]
        prompts.append(str(kwargs.get("prompt", "")))
        return {"response": "[P]g:x;c:y;s:z;r:k\n[A]ok"}

    monkeypatch.setattr(engine.client, "generate", fake_generate)

    result = engine.run('json only: {"ok":true,"why":"short"}')

    assert result.bypassed is False
    assert result.answer == "ok"
    assert prompts and prompts[0].startswith("Generate a compact internal plan prefix")
