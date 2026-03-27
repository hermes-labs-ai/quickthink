from quickthink.inline_protocol import extract_plan_and_answer


def test_extract_plan_and_answer() -> None:
    raw = "[P]g:solve;c:constraints;s:direct_reasoning;r:verify_output\n[A]Final answer here"
    plan, answer = extract_plan_and_answer(raw)
    assert plan == "g:solve;c:constraints;s:direct_reasoning;r:verify_output"
    assert answer == "Final answer here"


def test_extract_fallback_when_tags_missing() -> None:
    raw = "Final answer only"
    plan, answer = extract_plan_and_answer(raw)
    assert plan is None
    assert answer == "Final answer only"
