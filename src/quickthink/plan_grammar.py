from __future__ import annotations

import re

_PLAN_RE = re.compile(
    r"^g:([a-z0-9_,-]{1,64});c:([a-z0-9_,-]{1,64});s:([a-z0-9_,-]{1,64});r:([a-z0-9_,-]{1,64})$"
)
_TOKEN_RE = re.compile(r"[a-z0-9_]+")


def estimate_plan_tokens(plan: str) -> int:
    return len(_TOKEN_RE.findall(plan.lower()))


def normalize_plan(raw: str) -> str:
    line = raw.strip().splitlines()[0] if raw.strip() else ""
    return line.strip().lower().replace(" ", "")


def is_valid_plan(plan: str, budget_tokens: int) -> bool:
    normalized = normalize_plan(plan)
    if not _PLAN_RE.match(normalized):
        return False
    return estimate_plan_tokens(normalized) <= budget_tokens
