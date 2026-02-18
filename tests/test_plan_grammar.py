from quickthink.plan_grammar import estimate_plan_tokens, is_valid_plan, normalize_plan


def test_normalize_plan() -> None:
    raw = "G:solve;C:constraints;S:direct_reasoning;R:verify_output\nextra"
    assert normalize_plan(raw) == "g:solve;c:constraints;s:direct_reasoning;r:verify_output"


def test_valid_plan_within_budget() -> None:
    plan = "g:inverse_roles;c:plausible_behavior;s:flip_control_axis;r:avoid_overreach"
    assert is_valid_plan(plan, budget_tokens=8)
    assert estimate_plan_tokens(plan) == 8


def test_invalid_plan_missing_key() -> None:
    plan = "g:inverse_roles;c:plausible_behavior;s:flip_control_axis"
    assert not is_valid_plan(plan, budget_tokens=8)
