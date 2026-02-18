from __future__ import annotations

import re

from .plan_grammar import normalize_plan

_INLINE_RE = re.compile(r"\[P\](.*?)\[A\](.*)", re.DOTALL)


def extract_plan_and_answer(raw: str) -> tuple[str | None, str]:
    text = raw.strip()
    match = _INLINE_RE.search(text)
    if not match:
        return None, text

    plan = normalize_plan(match.group(1))
    answer = match.group(2).strip()
    return plan, answer
