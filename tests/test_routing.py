from quickthink.config import QuickThinkConfig
from quickthink.routing import complexity_score, should_bypass


def test_low_complexity_bypasses() -> None:
    config = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    bypass, score, budget = should_bypass("What is 2+2?", config)
    assert bypass
    assert score <= 1
    assert budget == config.min_plan_budget_tokens


def test_high_complexity_uses_plan() -> None:
    config = QuickThinkConfig.with_model_profile("qwen2.5:1.5b")
    prompt = (
        "Design a step-by-step strategy and compare tradeoffs for a robust JSON parser "
        "with malformed inputs, returning a schema and bullet list."
    )
    bypass, score, budget = should_bypass(prompt, config)
    assert not bypass
    assert score >= 3
    assert budget >= 12


def test_complexity_score_signals() -> None:
    prompt = "Could you compare and optimize this architecture with a table output?"
    assert complexity_score(prompt) >= 3
