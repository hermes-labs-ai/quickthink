from __future__ import annotations


def make_plan_prompt(user_prompt: str, budget: int) -> str:
    return (
        "You are a compressed planning module. Produce only one ultra-compact plan line.\n"
        "Rules:\n"
        f"- Max keyword tokens: {budget}\n"
        "- Lowercase only\n"
        "- No spaces\n"
        "- No prose\n"
        "- No markdown\n"
        "- Exactly this format and key order: g:<...>;c:<...>;s:<...>;r:<...>\n"
        "- Use slugs with [a-z0-9_,-]\n\n"
        f"User task:\n{user_prompt}\n"
    )


def make_answer_prompt(user_prompt: str, plan: str) -> str:
    return (
        "You are an assistant. Use the compact plan internally and answer directly.\n"
        "Do not reveal internal planning.\n"
        "Return only the final answer.\n\n"
        f"Internal plan:\n{plan}\n\n"
        f"User task:\n{user_prompt}\n"
    )


def make_plan_repair_prompt(user_prompt: str, bad_plan: str, budget: int) -> str:
    return (
        "Repair the plan to valid compact grammar. Return one line only.\n"
        f"Budget: {budget} keyword tokens max.\n"
        "Required format: g:<...>;c:<...>;s:<...>;r:<...>\n"
        "Rules: lowercase, no spaces, keys in exact order, [a-z0-9_,-] only.\n\n"
        f"User task:\n{user_prompt}\n\n"
        f"Invalid plan:\n{bad_plan}\n"
    )


def make_inline_plan_answer_prompt(user_prompt: str, budget: int, continuity_hint: str | None = None) -> str:
    hint_line = ""
    if continuity_hint:
        hint_line = (
            "Optional continuity hint is provided below. Use it only if clearly useful.\n"
            f"Hint: {continuity_hint}\n"
        )
    return (
        "Generate a compact internal plan prefix and then the answer in one response.\n"
        "Output format must be exactly:\n"
        "[P]g:<...>;c:<...>;s:<...>;r:<...>\n"
        "[A]<final answer text>\n"
        "Rules for [P]:\n"
        f"- max keyword tokens: {budget}\n"
        "- lowercase\n"
        "- no spaces\n"
        "- grammar keys in order: g,c,s,r\n"
        "- chars allowed: [a-z0-9_,-:;]\n"
        "Rules for [A]:\n"
        "- direct final answer\n"
        "- do not mention internal planning\n"
        "- no extra section headers\n"
        f"{hint_line}\n"
        f"User task:\n{user_prompt}\n"
    )
