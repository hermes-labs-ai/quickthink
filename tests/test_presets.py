from quickthink.config import PRESET_PROFILES, SUPPORTED_MODELS, QuickThinkConfig


def test_supported_models_are_stable() -> None:
    assert SUPPORTED_MODELS == ("qwen2.5:1.5b", "mistral:7b", "gemma3:27b")


def test_apply_preset_changes_routing_shape() -> None:
    cfg = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    cfg.apply_preset("fast")
    assert cfg.preset == "fast"
    assert cfg.max_plan_budget_tokens == PRESET_PROFILES["fast"]["max_plan_budget_tokens"]


def test_apply_unknown_preset_raises() -> None:
    cfg = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    try:
        cfg.apply_preset("unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
