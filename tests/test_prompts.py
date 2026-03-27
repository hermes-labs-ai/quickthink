from quickthink.prompts import make_answer_prompt, make_inline_plan_answer_prompt, make_plan_prompt


def test_plan_prompt_contains_budget_and_task() -> None:
    prompt = make_plan_prompt("Solve 2+2", 12)
    assert "12" in prompt
    assert "Solve 2+2" in prompt


def test_answer_prompt_hides_planning_contract() -> None:
    prompt = make_answer_prompt("Question", "plan: foo")
    assert "Do not reveal internal planning" in prompt
    assert "plan: foo" in prompt


def test_inline_prompt_enforces_protocol() -> None:
    prompt = make_inline_plan_answer_prompt("Question", 8, continuity_hint="ctx:goal_json")
    assert "[P]g:<...>;c:<...>;s:<...>;r:<...>" in prompt
    assert "[A]<final answer text>" in prompt
    assert "ctx:goal_json" in prompt
